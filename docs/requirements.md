

# Requirements and Asset Register   Campus Room Booking System



## 1. Purpose and Scope



The Campus Room Booking System is a Python application

that allows university students to reserve study rooms,

manage their bookings, and generate booking confirmations.



The system focuses on authentication, authorization,

resource ownership, secure service communication,

and controlled vulnerability investigations.



The application will use synthetic data and seeded

accounts. Public hosting, user registration, payment

processing, and email delivery are outside the scope.



## 2. Users and Roles



| User | Role |

|---|---|

| Amin | Student |

| Casper | Student |

| Frank | Student |

| Rasmus | Administrator |



Students can manage their own bookings and confirmations.



The administrator can manage rooms and view system-wide

booking metadata but does not automatically have access

to other users' private booking confirmations.



## 3. Functional Requirements



| ID | Requirement | Acceptance Criteria |

|---|---|---|

| FR1 | User authentication | Seeded users can log in with valid credentials |

| FR2 | View available rooms | Authenticated users can retrieve room availability |

| FR3 | Create bookings | Users can reserve an available room |

| FR4 | Manage bookings | Users can view and cancel their own bookings |

| FR5 | Generate confirmations | All three services participate in confirmation generation |

| FR6 | Retrieve confirmations | Users can retrieve their own confirmations |

| FR7 | Admin room management | Only the administrator can create or modify rooms |

| FR8 | Admin audit metadata | Only the administrator can retrieve system wide booking metadata |

| FR9 | Prevent booking conflicts | Overlapping active bookings for the same room are rejected |



## 4. Non-Functional Requirements



| ID | Requirement | Verification |

|---|---|---|

| NFR1 | Three independent services | Verify three separate running Docker containers communicating over HTTP |

| NFR2 | Authentication enforcement | Requests without valid authentication are rejected |

| NFR3 | Resource level authorization | Cross user booking and confirmation access is denied |

| NFR4 | Least privilege | Services receive only the authority required for their operations |

| NFR5 | Secure service communication | Scoped credentials bind service, action, resource and expiration |

| NFR6 | Input validation | Malformed and unauthorized input is rejected |

| NFR7 | Reproducible builds | Documented builds use approved and pinned dependencies |

| NFR8 | Dependency integrity | Unapproved or modified dependency artifacts are rejected |

| NFR9 | Automated testing | Functional and authorization tests run in a fresh environment |

| NFR10 | CI/CD security gates | Jenkins runs on pushes and pull requests and blocks defined failures |

| NFR11 | Evidence preservation | Tests, security findings and pipeline results are saved |

| NFR12 | Auditability | Security relevant operations produce useful logs without exposing credentials |



## 5. Asset Register



| ID | Asset | Responsible Component | Security Objective | Main Threat |

|---|---|---|---|---|

| A1 | Student bookings | Booking Service | Confidentiality and integrity | Unauthorized access or modification |

| A2 | Booking confirmations | Booking Service | Confidentiality and integrity | Cross user disclosure |

| A3 | Room availability | Booking Service | Integrity and availability | Conflicting or unauthorized bookings |

| A4 | User credentials | Application API | Confidentiality | Credential theft or impersonation |

| A5 | Authentication tokens | Application API | Confidentiality and integrity | Token theft or forgery |

| A6 | Service authorization credentials | Application API issues; receiving services verify | Integrity and limited authority | Cross service privilege abuse |

| A7 | SQLite database | Booking Service | Confidentiality, integrity and availability | Unauthorized access or data corruption |

| A8 | External helper package | Confirmation Service | Integrity | Supply-chain tampering |

| A9 | Audit and test evidence | Development and CI environment | Integrity and traceability | Missing or altered evidence |



## 6. Component Responsibilities



### Component 1 - Application API



- Authenticates users.

- Establishes user identity and role.

- Coordinates booking and confirmation requests.

- Issues scoped and time-limited authorization credentials.

- Does not access SQLite directly.



### Component 2 - Booking Service



- Owns the SQLite database.

- Stores rooms, bookings and confirmations.

- Checks room availability and booking conflicts.

- Enforces ownership and administrator permissions.

- Independently validates internal authorization requests.



### Component 3 - Confirmation Service



- Receives authorized confirmation jobs.

- Retrieves only the permitted booking.

- Generates confirmations using the installed helper package.

- Saves results through the Booking Service.

- Has no direct SQLite database access.



## 7. Data Flow



The primary confirmation workflow involves all three

application components:



1. The user authenticates through the Application API.

2. The user requests confirmation of an owned booking.

3. The API verifies user authority and creates limited

&#x20;  authorization credentials.

4. The API sends an authorized job to Confirmation Service.

5. Confirmation Service requests the permitted booking

&#x20;  from Booking Service.

6. Booking Service independently verifies the permissions.

7. Confirmation Service uses the installed helper package

&#x20;  to generate the confirmation.

8. Confirmation Service stores the result through Booking

&#x20;  Service using job scoped authorization.

9. The user retrieves the result through Application API.



The system architecture and trust boundaries are shown

in the diagrams stored under docs/diagrams/.



## 8. Planned Security Investigations



The project will investigate:



- V1: Insecure Direct Object Reference (IDOR).

- V2: Privilege Escalation.

- V3: Mass Assignment.

- V4: Cross-Service Authorization Bypass.



The first three vulnerability types must be confirmed

against the course vulnerability catalog.



Each experiment will include a vulnerable version,

a controlled demonstration, a security fix, and a

regression test.



## 9. Requirements Gate Review



The requirements phase is ready for approval when:



- Functional operations are documented.

- Non functional requirements are defined.

- The asset register is complete.

- All three independent services have distinct responsibilities.

- User roles and resource ownership rules are defined.

- An access-control matrix exists.

- A STRIDE threat analysis exists.

- Architecture and data-flow diagrams are documented.

- Relevant threats have proposed controls and planned tests.



Gate decision: PENDING REVIEW



The gate decision will be updated after reviewing the

requirements documents and confirming their consistency.



## 10. Traceability and Evidence



The development process follows:



Asset -> Threat -> Requirement/Control ->

Lifecycle Activity -> Test/Evidence -> Gate Decision



Evidence will be collected using Git commits, automated

tests, vulnerability demonstrations, security scans,

Jenkins results, and documentation.



The final report will reference these artifacts to

explain security decisions and demonstrate compliance

with the assignment requirements.




