# ctime

## Goals

1. Users:
    1. Create schedule/availability
    2. Request days off
        1. Allow for comments/brief descriptions of why
        2. All requests are subject to approval based on company needs
        3. Blockout dates, Minimum Notice Periods, Maximum number of consecutive days off
    3. Edit their profile
    4. Dashboard
        1. Information on next shift
        2. Information on requested days off status
        3. Full schedule for company/team
2. Admins:
    1. Create schedule/availability for users
        1. Pagination on list/grid of users
    2. Approve/Reject days off
    3. Edit user profiles
    4. Dashboard
        1. Information on company/team
        2. Full schedule
3. Security:
    1. Add password confirmation field in RegisterForm class
    2. Implement password strength validation (add Length, Regexp validators)
    3. Add email verification mechanism
    4. Implement rate limiting for registration endpoint
    5. Add CAPTCHA or similar anti-automation measure
4. Modularity:
    1. Add environment variables for different operating modes
        1. Auto-approve time off
    2. Deploy as Docker container

---

## Potential Implementations

Goal 1.2.3:
[`web.py 248-269`](https://github.com/soarn/ctime/pull/1#pullrequestreview-2585551426)

```diff
             if time_off_form.validate_on_submit():
     date = time_off_form.date.data
     comment = time_off_form.comment.data
+    
+    # Check minimum notice period
+    if date <= datetime.now().date() + timedelta(days=7):
+        flash("Time off requests must be submitted at least 7 days in advance.", "warning")
+        return redirect(url_for("web.employee_dashboard"))
+    
+    # Check blackout dates
+    if is_blackout_date(date):
+        flash("Selected date is unavailable for time off requests.", "warning")
+        return redirect(url_for("web.employee_dashboard"))
+    
     existing_request = TimeOffRequest.query.filter_by(user_id=user_id, date=date).first()
```
