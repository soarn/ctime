# Changelog

## 0.1.0 (2025-02-26)


### ⚠ BREAKING CHANGES

* update user model and forms, improve time off request handling, and enhance admin dashboard interactions
* enhance user model and forms, add time off request functionality

### Features

* add admin dashboard templates for user management, schedule overview, and time off requests ([a52e97d](https://github.com/soarn/ctime/commit/a52e97d07f7b38018e048f4a1df3c3dab4920b84))
* add admin management page and enhance user role handling in admin panel ([da1eb57](https://github.com/soarn/ctime/commit/da1eb57d304ba7e2815a64d0cc44a19e92ae15ac))
* add API key authentication to db_models ([efc0696](https://github.com/soarn/ctime/commit/efc0696b5289070cc120b851afa871633a30e440))
* add cancel time off functionality and comment field to time off requests, improve visual clarity ([75e09f2](https://github.com/soarn/ctime/commit/75e09f236cc77990f2f3be30be8c26f95c42591f))
* add comment field to TimeOffRequest and update related forms ([8b7e829](https://github.com/soarn/ctime/commit/8b7e8291075ab3aec8dfe17221d75800b4e374cd))
* add endpoint to generate weekly schedule image for admins and enhance schedule data processing ([b6330e0](https://github.com/soarn/ctime/commit/b6330e052af8778e3f333bb5199538d1d13226b8))
* add error handling for fetching user data and updating profiles in employee dashboard ([484e9cd](https://github.com/soarn/ctime/commit/484e9cd4e7f768624b1b83f2511fc6a6cb1b20b6))
* add error handling for schedule time conversion in admin and employee dashboards ([455cab6](https://github.com/soarn/ctime/commit/455cab6fd3238a74fee029be9ec7684df22bd0c4))
* add error handling for user registration process ([43ccef6](https://github.com/soarn/ctime/commit/43ccef6fe254d167925b2fb301c2d4c81f8db92e))
* Add example .env file and update docker-compose for environment variable usage ([707bfe1](https://github.com/soarn/ctime/commit/707bfe156dccd69009a08048e53a70bc5060d34d))
* Add favicon and correct environment variable name in docker-compose ([275b3dd](https://github.com/soarn/ctime/commit/275b3ddd749ea16f8958c28e211d60362deb838d))
* add global context processor for user agent detection ([e5654e1](https://github.com/soarn/ctime/commit/e5654e174a88110871be82ab10fac523bf8c02a2))
* add new copyright footer to base template ([1de4bb8](https://github.com/soarn/ctime/commit/1de4bb8cce888ba6f5d6469c4e10a11502f27023))
* add QoL features, finish initial project ([637fb8e](https://github.com/soarn/ctime/commit/637fb8ee2c147b847298debca70ba80313dce39c))
* add rate limiting to API key generation route ([0e1823f](https://github.com/soarn/ctime/commit/0e1823f42d463efabcca69be71e24578429a52ad))
* add schedule template loading functionality and enhance form validation in employee dashboard ([43ea866](https://github.com/soarn/ctime/commit/43ea866935194ec8581f1309418aabc61f66863f))
* add Sentry initialization condition and implement rate limiting for admin routes ([0e8abca](https://github.com/soarn/ctime/commit/0e8abca86271bf932e6ae97bd68a34c264055039))
* Add Sentry user feedback integration for crashes ([e15e5e4](https://github.com/soarn/ctime/commit/e15e5e426d20be87b43615966651090b41f1404a))
* add slack_username field to User model and update related forms and templates ([af25618](https://github.com/soarn/ctime/commit/af25618f4cbbcdda381ab8f60307c02101f7016d))
* add time off request form and schedule editing functionality in employee dashboard ([964af23](https://github.com/soarn/ctime/commit/964af23d117d0904e44576e44ce3f4e038bd43d8))
* add today's date to employee dashboard and enhance profile page with API key management ([3f6a9c5](https://github.com/soarn/ctime/commit/3f6a9c5db62220621de8f239e7ec32a1b8ad5adb))
* add user profile management with Gravatar integration, implement dark mode, enhance navbar, work on UI design, improve home page ([12b1275](https://github.com/soarn/ctime/commit/12b12754d763b71b321f07893a38551f8e8cfc3d))
* add user timezone functionality with cookie management, update schedule displays, and enhance admin dashboard ([4a8e9c1](https://github.com/soarn/ctime/commit/4a8e9c10a636c89d992c925b7ccb3d2a5b64ec12))
* add validation for time off requests and update README with new policies ([90eb7fb](https://github.com/soarn/ctime/commit/90eb7fba534ac934997c53791d94bb5923973f4f))
* added has_day_off fields to schedule API ([21a83b9](https://github.com/soarn/ctime/commit/21a83b97981c2c43cbcbf12d5b82131e34c06f25))
* enhance admin dashboard with improved user management visuals and functionality ([ae72955](https://github.com/soarn/ctime/commit/ae729550df608c7983b88ec833c18c2999d85165))
* enhance admin management by preventing race conditions during role updates and improve user availability toggle functionality ([f75195e](https://github.com/soarn/ctime/commit/f75195eb1a5e90ee436c219bc5acf2a68d5a7569))
* enhance admin route security, improve logging, and streamline user registration role assignment ([6d028c2](https://github.com/soarn/ctime/commit/6d028c29b252e873b19a032c573288036e7b2bfd))
* enhance admin user management with role promotion handling and self-demotion prevention ([96ae131](https://github.com/soarn/ctime/commit/96ae131120808d879f91d14b5a5c7bc81486fe28))
* enhance API key authentication and update Swagger documentation for user and schedule endpoints ([17bd8ae](https://github.com/soarn/ctime/commit/17bd8ae4d6fec9dd031f6685e2dedf4d68fcc8ef))
* enhance app configuration with caching and security headers, improve theme toggle functionality, and add error handling for flash messages ([eaf04d1](https://github.com/soarn/ctime/commit/eaf04d1b4488748f7fc2371f8e417be91d3c03ce))
* enhance error handling and logging in admin and web routes, update week calculation to start on Monday ([88ba43b](https://github.com/soarn/ctime/commit/88ba43b2f68464611446b81f25ae2cffc0080db7))
* enhance password validation ([1991abc](https://github.com/soarn/ctime/commit/1991abcef61a8b07963f58453eca6e263ddfc2a3))
* enhance password validation in user registration and update user role comment ([ca6bffd](https://github.com/soarn/ctime/commit/ca6bffd2eccf21ed9a5a086df0d5242f8e1d2e7d))
* enhance schedule management by populating existing schedules and improving form handling ([4d173ee](https://github.com/soarn/ctime/commit/4d173ee25df3ab9906ec223bab747492573519ad))
* enhance schedule templates with improved layout and new schedule page ([453fb6c](https://github.com/soarn/ctime/commit/453fb6c5ca6740c17d81b6f74ab2af5c77ee7fbf))
* enhance UI with improved button styles, dark mode support, and updated hero section ([ab2de6b](https://github.com/soarn/ctime/commit/ab2de6b36dbc0260fadd20a1c456e3dbe8f2851d))
* enhance user management and scheduling features with sorting and new schedule route ([27dd81e](https://github.com/soarn/ctime/commit/27dd81edec4aa8d7c5a0f359aa4da2399199689d))
* enhance user model and forms, add time off request functionality ([48b9673](https://github.com/soarn/ctime/commit/48b9673e92aeaf155fbc89be568afc1e8fe1b398))
* enhance user registration and time off management with improved validation and error handling ([558d31f](https://github.com/soarn/ctime/commit/558d31f5cdb0d35c25e9f240fb3a171aee9107b6))
* implement API v1 routes and API key authentication ([10adb9b](https://github.com/soarn/ctime/commit/10adb9b3a337be394de28ef3870353691a884f91))
* implement changes requested by [@coderabbitai](https://github.com/coderabbitai) ([e11a341](https://github.com/soarn/ctime/commit/e11a3413cd02d0efc97d11d0122f3de1103e16fe))
* Implement new API routes ([aa69f44](https://github.com/soarn/ctime/commit/aa69f44d9db07de0f04a77ce70a117aae9556d2b))
* Implement OGP ([a3644e9](https://github.com/soarn/ctime/commit/a3644e985a0fc0509e36a5f2fac7f83e71672712))
* Implement required changes by [@coderabbitai](https://github.com/coderabbitai) ([4f88328](https://github.com/soarn/ctime/commit/4f88328689c149bf21600684c201ba5261f3c8b5))
* implement schedule system ([3b4d2d3](https://github.com/soarn/ctime/commit/3b4d2d342c8dc2715e66fdf473caef93a134a697))
* implement user management form and update user details functionality in admin panel ([46583ed](https://github.com/soarn/ctime/commit/46583ed51cfdc4454e09935d878d386ab8c14954))
* Improve API auth with the Bearer standard ([0f56f80](https://github.com/soarn/ctime/commit/0f56f801401abbb2dc7cb73245f90445932f9b04))
* improve form handling in admin dashboard for RTO form ([cfc29cb](https://github.com/soarn/ctime/commit/cfc29cb92380947d1cd5b008d79dde0e4fc804e7))
* improve schedule display and form handling in admin and employee dashboards ([b0f1e06](https://github.com/soarn/ctime/commit/b0f1e061db466ad1655d0ba57d229ff0e40b056a))
* Integrate Sentry for error tracking and add test error routes ([544a203](https://github.com/soarn/ctime/commit/544a2034bba3c7cfa2ac7b155a955e49dfcaf283))
* prevent admin demotion with failsafe if only one admin remains in the system ([3c05335](https://github.com/soarn/ctime/commit/3c05335dccc612b20cc19564b1958dcea56454ff))
* refactor templates to use new base layout and update URL routing ([3e6e1f4](https://github.com/soarn/ctime/commit/3e6e1f4fac37bf9f95daab8ef34782a349f6d01a))
* remove commented-out button elements in admin and employee dashboards for cleaner code ([02a7700](https://github.com/soarn/ctime/commit/02a7700126fd073860360b99651930e7df321c21))
* remove view_user template and update schedule handling with timezone conversion ([d7c770e](https://github.com/soarn/ctime/commit/d7c770eff1d00e2a2fcdea1f02f11823d035b5f7))
* update admin and user templates for improved layout and navigation ([e74c550](https://github.com/soarn/ctime/commit/e74c550b615370aa6793e97568f41976d00a94e2))
* update employee dashboard interactions and forms ([6e57d64](https://github.com/soarn/ctime/commit/6e57d641d92e06164e4e13428e1217ab20b48bb5))
* update favicon, give attribution to the Bootstrap project ([460ca7f](https://github.com/soarn/ctime/commit/460ca7f3d3bbac68884e293480f5637ef7c289e4))
* update user model and forms, improve time off request handling, and enhance admin dashboard interactions ([54d0a93](https://github.com/soarn/ctime/commit/54d0a93a4951da221da1cf4f45e61eb81b9bba32))


### Bug Fixes

* Actually query the time off requests ([d66a599](https://github.com/soarn/ctime/commit/d66a599a1b842dc7fe7e3cb7ea986e2bc62015dd))
* attempt to fix time off displays in API calls ([dcbbbc8](https://github.com/soarn/ctime/commit/dcbbbc8f3e563d948c59f8543128bd7044b05f30))
* correct typo in Dockerfile ([87ab699](https://github.com/soarn/ctime/commit/87ab699193a0d2b3bdc9b08d8fd77be408d05fad))
* debug day off in API ([a018d1e](https://github.com/soarn/ctime/commit/a018d1eeb010c87247c4fbb969e237b9d3d482a8))
* ensure schedule start and end times are only formatted when available ([18050d8](https://github.com/soarn/ctime/commit/18050d8d67ccb49bc1f88f080df578bd47f879c9))
* remove erroneous sentry code ([53bfa80](https://github.com/soarn/ctime/commit/53bfa80e9d8d6bc7f2de56755e6694c59a17e756))
* resolve the InvalidRequestError in the manage_admin function by using a nested transaction ([f8d455a](https://github.com/soarn/ctime/commit/f8d455a3f6cf88113fa283b22b51bb53475f8361))
* update datetime handling to use lambda for UTC in created_at and last_login fields ([d23c5d4](https://github.com/soarn/ctime/commit/d23c5d496185f25ec8ee4b08b52907c7f63b3719))
* update health check route to use SQLAlchemy text for database query ([08d0bba](https://github.com/soarn/ctime/commit/08d0bba6e8bf638a10ee7865a351e5bf7eb5e9d7))
* update timestamp handling to use UTC for created_at and last_login fields ([203c598](https://github.com/soarn/ctime/commit/203c5985118a32bc6f397a80d74f80b3876c5cca))


### Documentation

* add additional troubleshooting information for AWS deployment ([52dbee6](https://github.com/soarn/ctime/commit/52dbee63adc3476627d7756b504e451d02501b83))
* add README with project goals and user/admin functionalities ([aaba7c8](https://github.com/soarn/ctime/commit/aaba7c8bbe8cc1a9112b2e0652326c059c9e8221))
* Create LICENSE ([6193d16](https://github.com/soarn/ctime/commit/6193d16699b3ee2feb1623360bcd1d9222346d39))
* include basic information on deploying to AWS with AWS Copilot ([cc3de38](https://github.com/soarn/ctime/commit/cc3de38d82048b6370ab415da246a72035be00b9))
* Revise README to enhance project overview and feature descriptions ([79cc84b](https://github.com/soarn/ctime/commit/79cc84bf559bbd2615b9f617ddc843926ffac0cc))
* update copilot deployment instructions in README ([e9e6fd5](https://github.com/soarn/ctime/commit/e9e6fd5190a87fe9a2b4ac97efbcabbcfd65e1a3))
* update goals in README ([ed5cacc](https://github.com/soarn/ctime/commit/ed5cacc095a5945c630aee5c39b1f3e52679a573))
* update README to current project status ([60ff658](https://github.com/soarn/ctime/commit/60ff658dd7d3b36ae9f92833bf6d959f2284055d))
* update README to include cloning the repo ([4599101](https://github.com/soarn/ctime/commit/45991017bd82d5c183d3594420970a974f68f08a))
* update README to include file paths ([3c65596](https://github.com/soarn/ctime/commit/3c65596879830f6bfdd442fbc40569135c01ffcc))
* update README to include future ideas for security features and pagination for user management ([b0157dd](https://github.com/soarn/ctime/commit/b0157ddaaf685cee78f51cca5aeefc08432834bc))
* update README to reflect current issues and completed tasks ([6ed1cb7](https://github.com/soarn/ctime/commit/6ed1cb73c40d0136b430036a4eb2c8e628fb19b3))
* Update README with troubleshooting information ([c3527a0](https://github.com/soarn/ctime/commit/c3527a0ae792992abad44b7afe4baf740b3c9c27))
