# Quick Debug Reference - Student Form

## 🚀 How to Debug in 3 Steps

### Step 1: Open Django Console
```bash
python manage.py runserver
```
Keep this terminal visible!

### Step 2: Open Browser Console
- Press **F12** (or Ctrl+Shift+I)
- Click **Console** tab
- Check "Preserve log" ☑️

### Step 3: Try to Submit Form
Watch BOTH consoles for errors!

---

## 📊 What to Look For

### ✅ Success Pattern (Everything Working)

**Browser Console**:
```
Form LOADED ✓
FORM SUBMIT EVENT TRIGGERED
✓ Validation passed, submitting form...
```

**Django Console**:
```
✓ Form is VALID
✓ User created successfully
✓ Student created successfully
✓✓✓ Student addition completed successfully!
```

### ❌ Common Problems

#### Problem: Form Won't Submit

**Browser Shows**:
```javascript
✗ Required field empty: email
FORM VALIDATION FAILED
```
**Fix**: Fill all required fields (marked with *)

---

#### Problem: "Form is INVALID"

**Django Shows**:
```python
✗ Form is INVALID
Form errors: {"email": ["This email is already registered"]}
```
**Fix**: Check the specific field error and correct it

---

#### Problem: Supabase Error

**Django Shows**:
```python
✗ Document upload error: Supabase configuration missing
```
**Fix**: Set up Supabase in `.env` file:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-key-here
```

---

#### Problem: Email Not Sending

**Django Shows**:
```python
✗ Email sending error: SMTPAuthenticationError
```
**Fix**: Check email settings in `.env`:
```env
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## 🔍 Quick Checks

Before asking for help, verify:

- [ ] Django server is running (terminal shows log output)
- [ ] Browser console is open (F12)
- [ ] All required fields are filled (*)
- [ ] Django console shows "POST request received"
- [ ] Check where the ✗ symbol appears (that's where it fails)

---

## 📝 Copy This Info When Asking for Help

1. **From Browser Console** (Ctrl+A, Ctrl+C):
```
[Paste everything from browser console here]
```

2. **From Django Console** (copy between the ====== lines):
```
[Paste Django log output here]
```

3. **What you were doing**:
- Trying to add new student / edit student ID: ___
- Filled fields: ___
- Uploaded files: ___

---

## 🎯 Most Common Issue

**Symptom**: Form submits but nothing happens

**Check Django Console For**:
```python
✗ Form is INVALID
  - roll_number: ['This field is required.']
```

**Solution**: The form field might not be submitting properly. Check:
1. Field has a `name` attribute
2. Field is inside `<form>` tags
3. Field is not disabled
4. Value is actually entered

---

## 💡 Pro Tips

1. **Clear browser cache** if JavaScript isn't loading:
   - Ctrl+Shift+Delete → Clear cache
   - Or Ctrl+F5 (hard refresh)

2. **Check Network tab** in browser:
   - See if POST request is being sent
   - Check request payload
   - Check response status (should be 200 or 302)

3. **Test with minimal data first**:
   - Fill only required fields
   - Don't upload files initially
   - Add complexity once basic form works

---

## 📚 Full Documentation

For detailed information, see:
- `DEBUG_LOGS_GUIDE.md` - Complete logging guide
- `INSTALLATION_STEPS.md` - Setup instructions
- `SUPABASE_SETUP_GUIDE.md` - Supabase configuration

---

**Remember: The logs will tell you EXACTLY where it fails! 🎯**



