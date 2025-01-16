# ctime

## Goals

1. Users:
    1. Create schedule/availability
    2. Request days off
        1. Allow for comments/brief descriptions of why
        2. All requests are subject to approval based on company needs
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