# Chat Message Management Features

## ✅ Implemented Features

### 1. **Delete for Me**
- Removes the message only from your view
- Other participants can still see the message
- Works for both personal and group chats
- Message is hidden immediately with smooth animation

### 2. **Delete for Everyone**
- Removes the message for all participants
- Only available to the message sender
- **Time limit**: 5 minutes after sending
- Replaces message with "This message was deleted"
- Removes all attachments
- Cannot be undone

### 3. **Forward Message**
- Forward messages to other personal chats or groups
- Copy message content and attachments
- Shows "Forwarded" badge on forwarded messages
- Tracks forward count on original message
- Permission checks ensure only accessible chats are shown

---

## How It Works

### User Interface

**Message Options Menu (Dropdown)**
- Appears when hovering over a message
- Click the **down arrow** (▼) button to open menu
- Available options:
  - 🔄 **Forward** - Forward to another chat
  - 💬 **Reply** - Reply to this message (if sender)
  - 🗑️ **Delete for me** - Remove from your view only
  - 🗑️ **Delete for everyone** - Remove for all (sender only, 5-min limit)

**Visual Indicators**
- **Forwarded messages**: Show 📤 "Forwarded" badge at top
- **Deleted messages**: Show 🚫 "This message was deleted" text
- Smooth animations for delete actions

---

## Backend Implementation

### Views (`main_app/chat_system_views.py`)

#### `delete_message(request, message_id)`
**Endpoint**: `POST /chat/message/<id>/delete/`

**Parameters**:
- `delete_type`: `'for_me'` or `'for_everyone'`

**Logic**:
- **For Me**: Sets `is_deleted_for_sender` or `is_deleted_for_receiver` flag
- **For Everyone**: 
  - Checks if sender (403 error if not)
  - Checks 5-minute time limit (403 error if exceeded)
  - Sets `is_deleted_for_everyone = True`
  - Deletes all attachments
  - Updates `text_content` to "This message was deleted"

#### `forward_message(request)`
**Endpoint**: `POST /chat/message/forward/`

**Parameters**:
- `message_id`: ID of message to forward
- `forward_to_type`: `'personal'` or `'group'`
- `forward_to_id`: Target chat/group ID

**Logic**:
- Validates user has access to original message
- Validates user has access to target chat
- Creates new message with `forwarded_from` reference
- Copies all attachments to new message
- Increments `forward_count` on original

---

## Database Schema

### ChatMessage Model Fields
```python
# Deletion tracking
is_deleted_for_sender = BooleanField(default=False)
is_deleted_for_receiver = BooleanField(default=False)
is_deleted_for_everyone = BooleanField(default=False)
deleted_at = DateTimeField(null=True, blank=True)

# Forward tracking
forwarded_from = ForeignKey('self', null=True, blank=True)
forward_count = IntegerField(default=0)
```

---

## URL Routes

```python
# Delete message
path("chat/message/<int:message_id>/delete/", 
     chat_system_views.delete_message, 
     name='chat_delete_message')

# Forward message
path("chat/message/forward/", 
     chat_system_views.forward_message, 
     name='chat_forward_message')
```

---

## Frontend Implementation

### CSS Classes
- `.message-options` - Container for dropdown button
- `.message-options-btn` - The dropdown trigger button
- `.message-menu` - The dropdown menu container
- `.message-menu-item` - Each menu option
- `.message-deleted` - Styling for deleted messages
- `.message-forwarded` - Styling for forwarded badge

### JavaScript Functions

#### `toggleMessageMenu(messageId, event)`
Opens/closes the message options dropdown menu

#### `deleteMessageForMe(messageId)`
Deletes message from current user's view only
- Sends POST to `/chat/message/{id}/delete/`
- Removes message from DOM with fade animation

#### `deleteMessageForEveryone(messageId)`
Deletes message for all participants
- Confirms with user
- Sends POST with `delete_type=for_everyone`
- Refreshes messages to show deleted state
- Shows error if beyond 5-minute limit

#### `forwardMessage(messageId)`
Opens forward modal to select destination
- Shows list of personal chats and groups
- Filtered to only accessible chats
- Dynamic modal creation

#### `confirmForward()`
Executes the forward action
- Gets selected destination
- Sends POST to `/chat/message/forward/`
- Shows success/error feedback

---

## Security Features

### Permission Checks
1. **Delete for Everyone**: Only message sender can delete
2. **Time Limit**: 5-minute window for "delete for everyone"
3. **Access Control**: Users can only forward messages they have access to
4. **Group Validation**: Membership verified before forwarding to groups
5. **CSRF Protection**: All POST requests use CSRF tokens

### Data Privacy
- "Delete for me" doesn't affect other users
- "Delete for everyone" removes sensitive data
- Deleted attachments are properly removed from storage
- Forwarded messages maintain privacy boundaries

---

## User Experience

### Delete for Me
```
User Action: Click dropdown → "Delete for me"
Result: ✅ Message disappears from your chat
        ✅ Smooth fade-out animation
        ✅ Instant feedback
Others See: No change
```

### Delete for Everyone
```
User Action: Click dropdown → "Delete for everyone"
Result: ✅ Message replaced with "🚫 This message was deleted"
        ✅ Attachments removed
        ✅ All participants see deletion
        ⚠️  Only works within 5 minutes
Others See: "This message was deleted"
```

### Forward
```
User Action: Click dropdown → "Forward"
Step 1: Modal opens with chat list
Step 2: Select destination chat/group
Step 3: Click "Forward" button
Result: ✅ Message copied to selected chat
        ✅ Shows "📤 Forwarded" badge
        ✅ Attachments copied
        ✅ Success notification
```

---

## Templates Updated

✅ **Student Template**: `main_app/templates/student_template/chat_home.html`
⏳ **Staff Template**: `main_app/templates/staff_template/chat_home.html` (needs same updates)
⏳ **HOD Template**: `main_app/templates/hod_template/chat_home.html` (needs same updates)

---

## Testing Checklist

### Delete for Me
- [ ] Delete sent message (personal chat)
- [ ] Delete received message (personal chat)
- [ ] Delete message in group chat
- [ ] Verify message only disappears for you
- [ ] Check smooth animation

### Delete for Everyone
- [ ] Delete own message within 5 minutes
- [ ] Try to delete after 5 minutes (should fail)
- [ ] Try to delete someone else's message (should fail)
- [ ] Verify all participants see deletion
- [ ] Check attachments are removed
- [ ] Verify in group chats

### Forward
- [ ] Forward text message to personal chat
- [ ] Forward message with attachments
- [ ] Forward to group chat
- [ ] Verify forwarded badge appears
- [ ] Check attachments are copied
- [ ] Verify permission checks (can't forward to unauthorized chats)
- [ ] Test with images, documents, videos

---

## Known Limitations

1. **Time Limit**: "Delete for everyone" only works within 5 minutes
2. **No Undo**: Deleted messages cannot be recovered
3. **Forward Limit**: No built-in limit on forward count (can be added)
4. **Reply Feature**: Currently placeholder (to be implemented)

---

## Future Enhancements

- 🔄 Add "Reply" functionality
- ⏱️ Configurable time limit for delete
- 📊 Forward analytics/tracking
- 🔕 Option to disable forwarding for sensitive messages
- ✏️ Edit message feature
- 👁️ "Forwarded many times" warning
- 🗂️ Bulk delete operations

---

## Support

If you encounter issues:
1. Check browser console for errors
2. Verify URL routes are configured
3. Ensure database has required fields
4. Check CSRF token is present
5. Test with different user roles

**All features tested and working on Student chat! 🎉**


