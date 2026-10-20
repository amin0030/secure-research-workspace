# STRIDE Threat Model  Campus Room Booking System



## 1\. Purpose



This document identifies potential security threats to the Campus Room Booking System using the STRIDE threat-modelling methodology.



The purpose is to identify threats before implementation, define security controls, and establish tests that can provide evidence that the controls work.



The threat model focuses on authentication, authorization, booking ownership, communication between services, and external dependencies.



## 2\. System Overview



The application consists of three independent Python services:



1. **Application API:** Authenticates users, checks roles, coordinates requests, and issues scoped authorization credentials.
2. **Booking Service:** Manages rooms, bookings, and confirmations, enforces access control, and owns the SQLite database.
3. **Confirmation Service:** Generates booking confirmations using an installed external Python helper package.



The application uses four seeded accounts:



* Amin: Student
* Casper: Student
* Frank: Student
* Rasmus: Administrator



Students can manage their own bookings. The administrator can additionally manage rooms and access booking metadata, but does not automatically have access to other users' private booking confirmations.



## 3\. Protected Assets



| Asset | Security objective |

|---|---|

| Student bookings | Confidentiality, integrity |

| Booking confirmations | Confidentiality, integrity |

| Room availability | Integrity, availability |

| User credentials | Confidentiality |

| Authentication tokens | Confidentiality, integrity |

| Service authorization credentials | Confidentiality, integrity |

| SQLite database | Confidentiality, integrity, availability |

| External helper package | Integrity |

| Security audit logs | Integrity, accountability |



## 4\. Trust Boundaries



**TB1: Users to Application API**



External clients must not be trusted. The API must validate authentication, roles, and user input.



**TB2: Application API to Booking Service**



The Booking Service must verify scoped authorization and resource permissions. Requests from the API are not automatically trusted.



**TB3: Application API to Confirmation Service**



The Confirmation Service must accept only authorized jobs and verify that the credentials match the requested operation.



**TB4: Confirmation Service to Booking Service**



The Booking Service must verify that a confirmation job is authorized to access the specific booking and perform the requested action.



**TB5: Confirmation Service to External Package**



The helper package is supplied software and must not be trusted with unrestricted access to protected resources.



**TB6: Booking Service to SQLite**



Only the Booking Service should access the database directly. Database queries must preserve integrity and ownership requirements.



## 5\. STRIDE Threat Analysis



| ID | STRIDE | Threat | Affected boundary | Security control | Planned evidence |

|---|---|---|---|---|---|

| S1 | Spoofing | An attacker impersonates Amin using invalid or forged authentication credentials | TB1 | Password hashing, signed tokens, expiration checks | Invalid and forged tokens are rejected |

| T1 | Tampering | Frank attempts to change the owner of a booking to Casper | TB1, TB2 | Server controlled ownership and strict input validation | Forged ownership field is rejected |

| R1 | Repudiation | A user denies cancelling a booking | TB1, TB2 | Audit logs recording user identity, booking ID, action and time | Cancellation produces an audit record |

| I1 | Information Disclosure | Amin accesses Casper's private booking by changing its ID | TB2 | Resource ownership validation | Cross user booking access is denied |

| D1 | Denial of Service | Repeated or oversized requests overload the application | TB1 | Input limits, timeouts and request limits | Oversized requests are rejected |

| E1 | Elevation of Privilege | Frank attempts to manage rooms using an administrator only endpoint | TB1, TB2 | Role-based access control enforced by API and Booking Service | Student receives HTTP 403 |

| E2 | Elevation of Privilege | Confirmation Service uses excessive service privileges to retrieve an unrelated booking | TB4 | Job scoped credentials and resource level authorization | Unrelated booking request is denied |

| T2 | Tampering | An unapproved or modified helper package is installed | TB5 | Dependency declarations and approved artifact verification | Altered dependency artifact is rejected |

| T3 | Tampering | Two overlapping bookings are accepted for the same room | TB6 | Transactional availability checking | Conflicting booking is rejected |



## 6\. Risk Assessment



The following qualitative risk levels are initial estimates. They will be reviewed during security testing.



| Threat ID | Likelihood | Impact | Initial priority |

|---|---|---|---|

| S1 | Medium | High | High |

| T1 | Medium | High | High |

| R1 | Medium | Medium | Medium |

| I1 | High | High | High |

| D1 | Medium | Medium | Medium |

| E1 | Medium | High | High |

| E2 | High | High | High |

| T2 | Medium | High | High |

| T3 | Medium | Medium | Medium |



Authorization violations affecting private bookings and administrator functions are considered high-priority threats.



## 7\. Planned Vulnerability Investigations



The implementation will investigate four deliberately introduced vulnerabilities.



### V1: Insecure Direct Object Reference (IDOR)



A student attempts to access another student's booking by changing the booking identifier.



**Security requirement:** Booking ownership must be verified on every protected resource operation.



### V2: Privilege Escalation



An ordinary student attempts to perform an administrator-only action, such as modifying room availability.



**Security requirement:** Administrative operations require independently verified administrator authority.



### V3: Mass Assignment



A student attempts to manipulate protected booking fields, such as the booking owner.



**Security requirement:** Ownership must be assigned by the server using the authenticated identity.



### V4: Cross Service Authorization Bypass



The Confirmation Service attempts to retrieve an unrelated booking using excessive internal service authority.



**Security requirement:** Authorization between services must be bound to the intended action, booking, job, and validity period.



The first three vulnerability types must be verified against the course vulnerability catalog before implementing the experiments.



Every vulnerability investigation will include an intentionally vulnerable version, evidence of the violation, a security fix, and a regression test.



## 8\. Secure Design Principles



### Least Privilege



Each service receives only the permissions necessary to perform its responsibilities.



The Confirmation Service must not have unrestricted database access or unrestricted access to all bookings.



### Complete Mediation



The Booking Service validates authorization for every protected booking and confirmation operation, including requests originating from other internal services.



### Fail Safe Defaults



Operations are rejected when authorization is missing, invalid, expired, or insufficient.



Unknown or unapproved dependencies are rejected during build verification.



## 9\. Security Testing Strategy



The security tests will verify:



* Invalid credentials cannot authenticate.
* Expired or forged authentication tokens are rejected.
* Students cannot access another student's bookings.
* Students cannot perform administrator only operations.
* Protected ownership fields cannot be manipulated.
* Confirmation jobs cannot access unrelated bookings.
* Unapproved dependency artifacts are rejected.
* Conflicting room bookings are prevented.
* Failed authorization attempts and relevant actions are logged without exposing credentials.



## 10\. SSDLC Gate Decisions



**Requirements gate:** The architecture, assets, trust boundaries, permissions and threats must be documented.



**Implementation/build gate:** The three components must build successfully, and unexpected or unapproved artifacts must be rejected.



**Testing gate:** All required functional and authorization tests must pass. Confirmed security violations must be fixed, and malformed artifacts must be rejected.



**Release gate:** Security evidence, Git history, dependency analysis and CI results must be reviewed before considering the implementation ready for release.



## 11\. Evidence Collection



Evidence will be collected throughout development and may include:



* Git commits and tags
* Security test results
* Screenshots of controlled vulnerability experiments
* Logs showing rejected unauthorized requests
* Dependency and static analysis reports
* Jenkins pipeline results
* Architecture and data-flow diagrams

