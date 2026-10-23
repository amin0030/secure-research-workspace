\# Access Control Matrix — Campus Room Booking System



\## 1. Purpose



This document defines which users and application services are authorized to perform operations in the Campus Room Booking System.



Authorization decisions must consider the authenticated identity, assigned role, requested action, resource ownership, and validity of the authorization credentials.



\## 2. Users and Roles



The application uses four seeded accounts:



| User | Role | Description |

|---|---|---|

| Amin | Student | Ordinary user |

| Casper | Student | Ordinary user |

| Frank | Student | Ordinary user |

| Rasmus | Administrator | Privileged user |



All students have the same permissions, but their bookings and confirmations remain private to their respective owners.



The administrator has a separate privileged role for managing room availability. Booking and confirmation operations require the student role.



\## 3. User Access Control Matrix




| Operation | Student | Administrator |
|---|---|---|
| Authenticate | Allow | Allow |
| View and search available rooms | Allow | Allow |
| Create own booking | Allow | Deny |
| View own booking | Allow | Deny |
| View another user's private booking | Deny | Deny |
| Cancel own booking | Allow | Deny |
| Cancel another user's booking | Deny | Deny |
| Generate confirmation for own booking | Allow | Deny |
| Retrieve own confirmation | Allow | Deny |
| Retrieve another user's confirmation | Deny | Deny |
| Activate or deactivate existing rooms | Deny | Allow |




The current implementation does not provide a system-wide booking metadata endpoint. Administrator privileges do not grant access to private student bookings or confirmations.



\## 4. Service Access Control Matrix



| Operation | Application API | Booking Service | Confirmation Service |

|---|---|---|---|

| Authenticate end users | Allow | Deny | Deny |

| Issue scoped authorization credentials | Allow | Deny | Deny |

| Access SQLite directly | Deny | Allow | Deny |

| Enforce booking ownership | Coordinate and verify user authority | Final authorization enforcement | Deny |

| Create or cancel bookings | Forward authorized requests | Validate and execute | Deny |

| Start confirmation jobs | Allow with user authorization | Deny | Execute authorized jobs |

| Retrieve booking for a confirmation job | Issue limited authority | Validate and return permitted booking | Scoped read only |

| Save generated confirmations | Coordinate requests | Validate and store | Scoped write only |

| Execute confirmation helper package | Deny | Deny | Allow |

| Manage room availability | Authorize admin requests | Enforce admin permission and execute | Deny |



The Application API cannot directly access the database. The Confirmation Service cannot directly access the database or obtain unrestricted access to bookings.



\## 5. Resource Ownership Rules



\*\*Rule 1: Booking ownership\*\*



Every booking belongs to exactly one authenticated user.



\*\*Rule 2: Student isolation\*\*



A student may read, cancel, or generate a confirmation only for their own booking.



\*\*Rule 3: Server-controlled ownership\*\*



The booking owner is determined from the authenticated identity and must not be trusted from user provided request fields.



\*\*Rule 4: Administrator permissions\*\*



The administrator may activate or deactivate existing rooms. The administrator cannot create student bookings or access students' private booking details or confirmations.



\*\*Rule 5: Independent service authorization\*\*



The Booking Service must enforce authorization for every protected operation, including requests received from the Confirmation Service.



\*\*Rule 6: Job scoped confirmation access\*\*



The Confirmation Service may retrieve and save information only for the booking and confirmation job identified by valid, limited authorization credentials.



\*\*Rule 7: Time limited authority\*\*



Service authorization credentials must specify their intended audience, action, resource or job, and expiration.



\*\*Rule 8: Deny by default\*\*



Any operation without sufficient authorization must be denied.



\## 6. Secure Design Principles



\### Least Privilege



Each user and service receives only the permissions required for its responsibilities.



\### Complete Mediation



The Booking Service independently checks every protected booking and confirmation operation.



\### Fail-Safe Defaults



Missing, invalid, expired, or insufficient permissions result in denied operations.



\## 7. Planned Authorization Tests



\- Amin can create and view his own bookings.

\- Amin cannot read or cancel Casper's bookings.

\- Frank cannot perform administrator only operations.

\- Rasmus can manage room availability.

\- Rasmus cannot automatically access Amin's private confirmation.

\- A request containing a forged booking owner is rejected.

\- The Confirmation Service cannot retrieve a booking unrelated to its authorized job.

\- Expired or incorrectly scoped authorization credentials are rejected.





