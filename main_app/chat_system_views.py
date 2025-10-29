"""
WhatsApp-like Chat System Views
Comprehensive chat functionality with groups, media sharing, and advanced features
"""
import json
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.http import JsonResponse
from django.db.models import Q, Count, Max, Prefetch
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.utils import timezone
from django.core.files.storage import default_storage
from PIL import Image
import mimetypes

from .models import (
    CustomUser, ChatGroup, ChatGroupMember, ChatMessage, 
    MessageAttachment, MessageReadReceipt, ChatConversation
)


@login_required
def chat_home(request):
    """Main chat interface - WhatsApp style"""
    user = request.user
    
    # Get user's personal conversations
    conversations = ChatConversation.objects.filter(
        Q(user1=user) | Q(user2=user)
    ).select_related('user1', 'user2').order_by('-last_message_at')
    
    # Get user's groups
    user_groups = ChatGroup.objects.filter(
        members__user=user,
        members__is_active=True
    ).prefetch_related(
        Prefetch('members', queryset=ChatGroupMember.objects.filter(is_active=True))
    ).annotate(
        unread_count=Count('group_messages', filter=Q(group_messages__is_read=False))
    ).order_by('-updated_at')
    
    # Get all users for new chat (filtered by role)
    if user.user_type == '1':  # HOD/Admin - can chat with everyone
        available_users = CustomUser.objects.exclude(id=user.id)
    elif user.user_type == '2':  # Faculty - can chat with admins, faculty, students
        available_users = CustomUser.objects.filter(
            Q(user_type='1') | Q(user_type='2') | Q(user_type='3')
        ).exclude(id=user.id)
    elif user.user_type == '3':  # Student - can chat with admins, faculty
        available_users = CustomUser.objects.filter(
            Q(user_type='1') | Q(user_type='2')
        ).exclude(id=user.id)
    else:
        available_users = CustomUser.objects.exclude(id=user.id)
    
    # Determine template based on user type
    if user.user_type == '3':
        template = 'student_template/chat_home.html'
    elif user.user_type == '2':
        template = 'staff_template/chat_home.html'
    elif user.user_type == '1':
        template = 'hod_template/chat_home.html'
    else:
        template = 'student_template/chat_home.html'
    
    context = {
        'page_title': 'Chats',
        'conversations': conversations,
        'user_groups': user_groups,
        'available_users': available_users,
    }
    
    return render(request, template, context)


@login_required
def get_chat_messages(request, chat_type, chat_id):
    """Get messages for a conversation or group"""
    user = request.user
    page = int(request.GET.get('page', 1))
    per_page = 50
    
    if chat_type == 'personal':
        # Personal chat
        other_user = get_object_or_404(CustomUser, id=chat_id)
        
        messages = ChatMessage.objects.filter(
            Q(sender=user, receiver=other_user, is_deleted_for_sender=False) |
            Q(sender=other_user, receiver=user, is_deleted_for_receiver=False)
        ).select_related('sender', 'receiver', 'reply_to__sender').prefetch_related(
            'attachments'
        ).order_by('-created_at')
        
        # Mark messages as read
        ChatMessage.objects.filter(
            sender=other_user, receiver=user, is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        chat_info = {
            'type': 'personal',
            'name': other_user.get_full_name(),
            'avatar': other_user.profile_pic.url if hasattr(other_user, 'profile_pic') and other_user.profile_pic else None,
            'user_type': other_user.user_type,
            'id': other_user.id,
        }
        
    elif chat_type == 'group':
        # Group chat
        group = get_object_or_404(ChatGroup, id=chat_id)
        
        # Check if user is member
        if not ChatGroupMember.objects.filter(group=group, user=user, is_active=True).exists():
            return JsonResponse({'error': 'Not a member of this group'}, status=403)
        
        messages = ChatMessage.objects.filter(
            group=group,
            is_deleted_for_everyone=False
        ).select_related('sender', 'reply_to__sender').prefetch_related(
            'attachments', 'read_receipts'
        ).order_by('-created_at')
        
        # Mark messages as read
        unread_messages = messages.filter(~Q(sender=user), is_read=False)
        for msg in unread_messages:
            MessageReadReceipt.objects.get_or_create(message=msg, user=user)
        
        # Get group members
        members = ChatGroupMember.objects.filter(group=group, is_active=True).select_related('user')
        is_admin = group.admins.filter(id=user.id).exists() or group.creator == user
        
        chat_info = {
            'type': 'group',
            'name': group.name,
            'description': group.description,
            'avatar': group.group_icon.url if group.group_icon else None,
            'id': group.id,
            'member_count': members.count(),
            'is_admin': is_admin,
            'members': [
                {
                    'id': m.user.id,
                    'name': m.user.get_full_name(),
                    'role': m.role,
                }
                for m in members
            ]
        }
    else:
        return JsonResponse({'error': 'Invalid chat type'}, status=400)
    
    # Paginate messages
    paginator = Paginator(messages, per_page)
    page_obj = paginator.get_page(page)
    
    # Format messages
    formatted_messages = []
    for msg in page_obj:
        message_data = {
            'id': msg.id,
            'sender_id': msg.sender.id,
            'sender_name': msg.sender.get_full_name(),
            'sender_avatar': msg.sender.profile_pic.url if hasattr(msg.sender, 'profile_pic') and msg.sender.profile_pic else None,
            'text_content': msg.text_content,
            'message_type': msg.message_type,
            'created_at': msg.created_at.isoformat(),
            'is_read': msg.is_read,
            'is_edited': msg.is_edited,
            'reactions': msg.reactions,
            'reply_to': {
                'id': msg.reply_to.id,
                'sender_name': msg.reply_to.sender.get_full_name(),
                'text_content': msg.reply_to.text_content[:50],
            } if msg.reply_to else None,
            'attachments': [
                {
                    'id': att.id,
                    'type': att.attachment_type,
                    'file_url': att.file.url,
                    'file_name': att.file_name,
                    'file_size': att.file_size_formatted,
                    'thumbnail': att.thumbnail.url if att.thumbnail else None,
                    'duration': att.duration,
                    'width': att.width,
                    'height': att.height,
                }
                for att in msg.attachments.all()
            ],
            'is_own_message': msg.sender == user,
        }
        formatted_messages.append(message_data)
    
    return JsonResponse({
        'chat_info': chat_info,
        'messages': formatted_messages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'total_pages': paginator.num_pages,
        'current_page': page,
    })


@login_required
@csrf_exempt
def send_message(request):
    """Send a text or media message"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    user = request.user
    chat_type = request.POST.get('chat_type')
    chat_id = request.POST.get('chat_id')
    text_content = request.POST.get('text_content', '')
    reply_to_id = request.POST.get('reply_to')
    
    try:
        # Create message
        message_data = {
            'sender': user,
            'text_content': text_content,
            'message_type': 'text',
        }
        
        if reply_to_id:
            message_data['reply_to_id'] = reply_to_id
        
        if chat_type == 'personal':
            receiver = get_object_or_404(CustomUser, id=chat_id)
            message_data['receiver'] = receiver
            
            # Update conversation
            ChatConversation.get_or_create_conversation(user, receiver)
            
        elif chat_type == 'group':
            group = get_object_or_404(ChatGroup, id=chat_id)
            
            # Check if user is member
            member = ChatGroupMember.objects.filter(group=group, user=user, is_active=True).first()
            if not member:
                return JsonResponse({'error': 'Not a member of this group'}, status=403)
            
            # Check if only admins can send
            if group.only_admins_can_send and member.role != 'admin':
                return JsonResponse({'error': 'Only admins can send messages'}, status=403)
            
            message_data['group'] = group
        else:
            return JsonResponse({'error': 'Invalid chat type'}, status=400)
        
        message = ChatMessage.objects.create(**message_data)
        
        # Handle file attachments
        files = request.FILES.getlist('attachments')
        for file in files:
            attachment_type = get_attachment_type(file.content_type)
            
            # Save file
            file_path = default_storage.save(
                f'chat_attachments/{timezone.now().strftime("%Y/%m/%d")}/{file.name}',
                file
            )
            
            # Get file size
            file_size = file.size
            
            # Create thumbnail for images
            thumbnail = None
            width = None
            height = None
            
            if attachment_type == 'image':
                try:
                    img = Image.open(file)
                    width, height = img.size
                    
                    # Create thumbnail
                    img.thumbnail((300, 300))
                    thumb_path = f'chat_thumbnails/{timezone.now().strftime("%Y/%m/%d")}/thumb_{file.name}'
                    thumb_full_path = default_storage.path(thumb_path)
                    os.makedirs(os.path.dirname(thumb_full_path), exist_ok=True)
                    img.save(thumb_full_path)
                    thumbnail = thumb_path
                except Exception as e:
                    print(f"Error creating thumbnail: {e}")
            
            # Create attachment
            MessageAttachment.objects.create(
                message=message,
                attachment_type=attachment_type,
                file=file_path,
                file_name=file.name,
                file_size=file_size,
                mime_type=file.content_type,
                thumbnail=thumbnail,
                width=width,
                height=height,
            )
            
            # Update message type if it has attachments
            if attachment_type != 'other':
                message.message_type = attachment_type
                message.save()
        
        return JsonResponse({
            'status': 'success',
            'message_id': message.id,
            'created_at': message.created_at.isoformat(),
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
def delete_message(request, message_id):
    """Delete message for me or for everyone"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    user = request.user
    delete_type = request.POST.get('delete_type', 'for_me')  # 'for_me' or 'for_everyone'
    
    try:
        message = get_object_or_404(ChatMessage, id=message_id)
        
        # Check permissions
        if delete_type == 'for_everyone':
            # Only sender can delete for everyone (within 7 days)
            if message.sender != user:
                return JsonResponse({'error': 'Only sender can delete for everyone'}, status=403)
            
            # Check if message is not too old (7 days)
            time_diff = timezone.now() - message.created_at
            if time_diff.days > 7:
                return JsonResponse({'error': 'Can only delete messages within 7 days'}, status=403)
            
            message.is_deleted_for_everyone = True
            message.deleted_at = timezone.now()
            message.save()
            
        else:  # Delete for me
            if message.sender == user:
                message.is_deleted_for_sender = True
            elif message.receiver == user:
                message.is_deleted_for_receiver = True
            elif message.group:
                # For group messages, we need a different approach
                # We can use a separate model or JSON field to track who deleted it
                pass
            else:
                return JsonResponse({'error': 'Cannot delete this message'}, status=403)
            
            message.save()
        
        return JsonResponse({'status': 'success', 'delete_type': delete_type})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
def create_group(request):
    """Create a new group"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    user = request.user
    
    try:
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        group_type = request.POST.get('group_type', 'private')
        member_ids = json.loads(request.POST.get('member_ids', '[]'))
        
        if not name:
            return JsonResponse({'error': 'Group name is required'}, status=400)
        
        # Create group
        group = ChatGroup.objects.create(
            name=name,
            description=description,
            group_type=group_type,
            creator=user,
        )
        
        # Add group icon if provided
        if 'group_icon' in request.FILES:
            group.group_icon = request.FILES['group_icon']
            group.save()
        
        # Add creator as admin member
        ChatGroupMember.objects.create(
            group=group,
            user=user,
            role='admin',
            added_by=user,
        )
        
        # Add creator as admin
        group.admins.add(user)
        
        # Add other members
        for member_id in member_ids:
            try:
                member_user = CustomUser.objects.get(id=member_id)
                ChatGroupMember.objects.create(
                    group=group,
                    user=member_user,
                    role='member',
                    added_by=user,
                )
                
                # Send system message
                ChatMessage.objects.create(
                    sender=user,
                    group=group,
                    text_content=f"{user.get_full_name()} added {member_user.get_full_name()}",
                    message_type='system',
                )
            except CustomUser.DoesNotExist:
                continue
        
        # Send welcome message
        ChatMessage.objects.create(
            sender=user,
            group=group,
            text_content=f"Welcome to {name}! 🎉",
            message_type='system',
        )
        
        return JsonResponse({
            'status': 'success',
            'group_id': group.id,
            'group_name': group.name,
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def group_settings(request, group_id):
    """Group settings page"""
    user = request.user
    group = get_object_or_404(ChatGroup, id=group_id)
    
    # Check if user is member
    member = ChatGroupMember.objects.filter(group=group, user=user, is_active=True).first()
    if not member:
        django_messages.error(request, "You are not a member of this group")
        return redirect('chat_home')
    
    is_admin = group.admins.filter(id=user.id).exists() or group.creator == user
    
    # Get all members
    members = ChatGroupMember.objects.filter(group=group, is_active=True).select_related('user')
    
    # Determine template based on user type
    if user.user_type == '3':
        template = 'student_template/group_settings.html'
    elif user.user_type == '2':
        template = 'staff_template/group_settings.html'
    elif user.user_type == '1':
        template = 'hod_template/group_settings.html'
    else:
        template = 'student_template/group_settings.html'
    
    context = {
        'page_title': f'{group.name} - Settings',
        'group': group,
        'members': members,
        'is_admin': is_admin,
        'is_creator': group.creator == user,
    }
    
    return render(request, template, context)


@login_required
@csrf_exempt
def update_group_settings(request, group_id):
    """Update group settings (admin only)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    user = request.user
    group = get_object_or_404(ChatGroup, id=group_id)
    
    # Check if user is admin
    is_admin = group.admins.filter(id=user.id).exists() or group.creator == user
    if not is_admin:
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    try:
        # Update group details
        if 'name' in request.POST:
            group.name = request.POST['name']
        if 'description' in request.POST:
            group.description = request.POST['description']
        if 'only_admins_can_send' in request.POST:
            group.only_admins_can_send = request.POST['only_admins_can_send'] == 'true'
        if 'allow_member_add' in request.POST:
            group.allow_member_add = request.POST['allow_member_add'] == 'true'
        
        # Update group icon
        if 'group_icon' in request.FILES:
            group.group_icon = request.FILES['group_icon']
        
        group.save()
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
def add_group_member(request, group_id):
    """Add member to group"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    user = request.user
    group = get_object_or_404(ChatGroup, id=group_id)
    
    # Check permissions
    member = ChatGroupMember.objects.filter(group=group, user=user, is_active=True).first()
    if not member:
        return JsonResponse({'error': 'Not a member of this group'}, status=403)
    
    is_admin = group.admins.filter(id=user.id).exists() or group.creator == user
    if not group.allow_member_add and not is_admin:
        return JsonResponse({'error': 'Only admins can add members'}, status=403)
    
    try:
        user_id = request.POST.get('user_id')
        new_member_user = get_object_or_404(CustomUser, id=user_id)
        
        # Check if already member
        existing_member = ChatGroupMember.objects.filter(group=group, user=new_member_user).first()
        if existing_member:
            if existing_member.is_active:
                return JsonResponse({'error': 'User is already a member'}, status=400)
            else:
                # Reactivate membership
                existing_member.is_active = True
                existing_member.joined_at = timezone.now()
                existing_member.added_by = user
                existing_member.save()
        else:
            # Create new membership
            ChatGroupMember.objects.create(
                group=group,
                user=new_member_user,
                role='member',
                added_by=user,
            )
        
        # Send system message
        ChatMessage.objects.create(
            sender=user,
            group=group,
            text_content=f"{user.get_full_name()} added {new_member_user.get_full_name()}",
            message_type='system',
        )
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
def remove_group_member(request, group_id, user_id):
    """Remove member from group (admin only)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    user = request.user
    group = get_object_or_404(ChatGroup, id=group_id)
    
    # Check if user is admin
    is_admin = group.admins.filter(id=user.id).exists() or group.creator == user
    if not is_admin:
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    try:
        member_user = get_object_or_404(CustomUser, id=user_id)
        
        # Cannot remove creator
        if member_user == group.creator:
            return JsonResponse({'error': 'Cannot remove group creator'}, status=400)
        
        # Remove member
        member = ChatGroupMember.objects.filter(group=group, user=member_user, is_active=True).first()
        if member:
            member.is_active = False
            member.left_at = timezone.now()
            member.save()
            
            # Send system message
            ChatMessage.objects.create(
                sender=user,
                group=group,
                text_content=f"{user.get_full_name()} removed {member_user.get_full_name()}",
                message_type='system',
            )
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
def leave_group(request, group_id):
    """Leave a group"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    user = request.user
    group = get_object_or_404(ChatGroup, id=group_id)
    
    # Cannot leave if creator
    if group.creator == user:
        return JsonResponse({'error': 'Creator cannot leave. Transfer ownership first or delete the group.'}, status=400)
    
    try:
        member = ChatGroupMember.objects.filter(group=group, user=user, is_active=True).first()
        if member:
            member.is_active = False
            member.left_at = timezone.now()
            member.save()
            
            # Remove from admins if admin
            group.admins.remove(user)
            
            # Send system message
            ChatMessage.objects.create(
                sender=user,
                group=group,
                text_content=f"{user.get_full_name()} left the group",
                message_type='system',
            )
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
def add_reaction(request, message_id):
    """Add emoji reaction to message"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    user = request.user
    emoji = request.POST.get('emoji')
    
    try:
        message = get_object_or_404(ChatMessage, id=message_id)
        message.add_reaction(user, emoji)
        
        return JsonResponse({'status': 'success', 'reactions': message.reactions})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
def remove_reaction(request, message_id):
    """Remove reaction from message"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    user = request.user
    
    try:
        message = get_object_or_404(ChatMessage, id=message_id)
        message.remove_reaction(user)
        
        return JsonResponse({'status': 'success', 'reactions': message.reactions})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_attachment_type(mime_type):
    """Determine attachment type from MIME type"""
    if mime_type.startswith('image/'):
        return 'image'
    elif mime_type.startswith('video/'):
        return 'video'
    elif mime_type.startswith('audio/'):
        return 'audio'
    elif mime_type in ['application/pdf', 'application/msword', 
                       'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                       'application/vnd.ms-excel',
                       'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                       'application/vnd.ms-powerpoint',
                       'application/vnd.openxmlformats-officedocument.presentationml.presentation']:
        return 'document'
    else:
        return 'other'


@login_required
def search_messages(request):
    """Search messages in all chats"""
    user = request.user
    query = request.GET.get('q', '')
    
    if not query:
        return JsonResponse({'results': []})
    
    # Search in personal messages
    personal_messages = ChatMessage.objects.filter(
        Q(sender=user, is_deleted_for_sender=False) | Q(receiver=user, is_deleted_for_receiver=False),
        text_content__icontains=query
    ).select_related('sender', 'receiver')[:20]
    
    # Search in group messages
    user_groups = ChatGroup.objects.filter(members__user=user, members__is_active=True)
    group_messages = ChatMessage.objects.filter(
        group__in=user_groups,
        is_deleted_for_everyone=False,
        text_content__icontains=query
    ).select_related('sender', 'group')[:20]
    
    results = []
    
    for msg in personal_messages:
        other_user = msg.receiver if msg.sender == user else msg.sender
        results.append({
            'type': 'personal',
            'chat_id': other_user.id,
            'chat_name': other_user.get_full_name(),
            'message_id': msg.id,
            'text': msg.text_content[:100],
            'created_at': msg.created_at.isoformat(),
        })
    
    for msg in group_messages:
        results.append({
            'type': 'group',
            'chat_id': msg.group.id,
            'chat_name': msg.group.name,
            'message_id': msg.id,
            'sender_name': msg.sender.get_full_name(),
            'text': msg.text_content[:100],
            'created_at': msg.created_at.isoformat(),
        })
    
    return JsonResponse({'results': results})

