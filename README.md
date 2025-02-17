# ctime

## Goals

- [ ] Users:
  - [x] Create schedule/availability
  - [x] Request days off
    - [x] Allow for comments/brief descriptions of why
    - [ ] All requests are subject to approval based on company needs
    - [ ] Blockout dates, Minimum Notice Periods, Maximum number of consecutive days off
    - [ ] Unknown error occurs if request off is for the current day, need to have this fixed.
    - [ ] Days are not controlled by timezone which could introduce issues in the future
  - [x] Edit their profile
  - [x] Dashboard
    - [x] Information on next shift
    - [x] Information on requested days off status
    - [ ] Full schedule for company/team
- [ ] Admins:
  - [x] Create schedule/availability for users
    - [ ] Pagination on list/grid of users
  - [x] Approve/Reject days off
  - [x] Edit user profiles
  - [x] Dashboard
    - [ ] Information on company/team
    - [x] Full schedule
- [ ] Security:
  - [ ] Add password confirmation field in RegisterForm class
  - [x] Implement password strength validation (add Length, Regexp validators)
  - [ ] Add email verification mechanism
  - [x] Implement rate limiting for registration endpoint
  - [ ] Add CAPTCHA or similar anti-automation measure
- [ ] Modularity:
  - [ ] Add environment variables for different operating modes
    - [ ] Auto-approve time off
  - [ ] Deploy as Docker container

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

## Building Locally

### Docker

1. Copy `.env.example` into `.env`.
   If you do not want to enable Sentry logging, you can leave that section blank
2. While in the root project folder, use the command `docker compose build`
3. Then use `docker compose --env-file .env up` to start the server
