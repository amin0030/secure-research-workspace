

# Requirements and Asset Register: Campus Room Booking System



## 1. Purpose and Scope



The Campus Room Booking System is a Python application that allows university students to search for available study rooms, create and manage bookings, and generate booking confirmations.



The application focuses on authentication, authorization, resource ownership, input validation, database security, and secure communication between independently running services.



The project will investigate three selected vulnerabilities from the course CWE vulnerability catalog and one additional vulnerability caused by composing independent application services.



The application will use synthetic data and seeded accounts.



Public hosting, user registration, payment processing, graphical interfaces, and email delivery are outside the scope.



## 2. Users and Roles



The system uses four seeded accounts.



| User | Role |

|---|---|

| Amin | Student |

| Casper | Student |

| Frank | Student |

| Rasmus | Administrator |



Students can search for study rooms, create bookings, manage their own reservations, and generate booking confirmations.


The administrator can activate or deactivate existing rooms. Booking and confirmation operations require the student role. The current implementation does not provide an administrator endpoint for system-wide booking metadata.




Administrative privileges do not automatically grant access to other students' private booking details or confirmations.



## 3. Functional Requirements



| ID | Requirement | Acceptance Criteria |

|---|---|---|

| FR1 | User authentication | Seeded users can log in with valid credentials |

| FR2 | View and search available rooms | Authenticated users can retrieve and search available study rooms |

| FR3 | Create bookings | Authenticated students can reserve available rooms using valid booking information |

| FR4 | Manage bookings | Students can view and cancel their own bookings |

| FR5 | Generate confirmations | All three application services participate in confirmation generation |

| FR6 | Retrieve confirmations | Students can retrieve confirmations belonging to their own bookings |

| FR7 | Administrator room management | Only the administrator can activate or deactivate existing rooms |

| FR8 | Restricted room management | Student requests to change room availability are rejected with HTTP 403 |

| FR9 | Prevent booking conflicts | Overlapping active bookings for the same room are rejected |

| FR10 | Validate booking times | Bookings with invalid start and end times are rejected |



The confirmation generation functionality must involve the Application API, Booking Service, and Confirmation Service.



The system must protect bookings and confirmations belonging to different users.



## 4. Non Functional and Security Requirements



| ID | Requirement | Verification |

|---|---|---|

| NFR1 | Three independent services | Verify three separately running Docker containers communicating through HTTP |

| NFR2 | Authentication enforcement | Requests requiring authentication reject missing or invalid credentials |

| NFR3 | Resource level authorization | Cross user booking and confirmation access is denied |

| NFR4 | Least privilege | Services receive only the permissions required for their responsibilities |

| NFR5 | Secure service authorization | Credentials bind the receiving service, action, resource or job, and expiration |

| NFR6 | Input validation | Invalid booking times and malformed input are rejected |

| NFR7 | SQL Injection prevention | Database queries use parameterized SQL statements |

| NFR8 | Server controlled ownership | Users cannot assign bookings to another user through input fields |

| NFR9 | Reproducible builds | Builds use declared and approved dependencies with pinned versions |

| NFR10 | Dependency integrity | Unexpected, modified, or unapproved dependency artifacts are rejected |

| NFR11 | Automated testing | Functional and authorization tests execute in a fresh environment |

| NFR12 | CI/CD security gates | Jenkins runs on pushes and pull requests and blocks defined security failures |

| NFR13 | Evidence preservation | Test results, security findings, and pipeline reports are saved as artifacts |

| NFR14 | Auditability | Relevant security operations produce logs without exposing credentials |

| NFR15 | Booking integrity | Concurrent or conflicting booking attempts cannot create overlapping active reservations |



The final implementation must enforce these requirements through application logic, established security libraries, database constraints, and deployment configuration.



## 5. Asset Register



| ID | Asset | Responsible Component | Security Objective | Main Threat |

|---|---|---|---|---|

| A1 | Student bookings | Booking Service | Confidentiality and integrity | Unauthorized access or modification |

| A2 | Booking confirmations | Booking Service | Confidentiality and integrity | Cross user information disclosure |

| A3 | Room availability | Booking Service | Integrity and availability | Invalid or conflicting bookings |

| A4 | User credentials | Application API | Confidentiality | Credential theft or impersonation |

| A5 | Authentication tokens | Application API | Confidentiality and integrity | Token theft or forgery |

| A6 | Service authorization credentials | Application API issues; receiving services verify | Integrity and limited authority | Cross service privilege abuse |

| A7 | SQLite database | Booking Service | Confidentiality, integrity and availability | SQL Injection or unauthorized data access |

| A8 | External Python helper package | Confirmation Service | Integrity | Supply chain tampering |

| A9 | Audit logs | Relevant services | Integrity and accountability | Missing or manipulated security records |

| A10 | Test and CI evidence | Development and CI environment | Integrity and traceability | Missing or modified evidence |



The Booking Service owns the protected room and booking records.



The Confirmation Service must not receive direct SQLite database access.



The Application API establishes user identity and issues limited authorization credentials.



## 6. Component Responsibilities



The application consists of three independently running Python services.



### Component 1: Application API



Responsibilities:



- Authenticate users.

- Establish user identity and role.

- Coordinate booking and confirmation requests.

- Authorize user requested operations.

- Issue scoped and time limited service authorization credentials.

- Forward requests to the appropriate internal service.



Security responsibilities:



- Reject unauthenticated requests.

- Protect authentication credentials.

- Verify administrator permissions.

- Avoid issuing credentials broader than the requested operation.



The Application API must not access SQLite directly.



### Component 2: Booking Service



Responsibilities:



- Own and manage the SQLite database.

- Store rooms, bookings, and confirmation records.

- Search for available study rooms.

- Create, retrieve, and cancel bookings.

- Validate booking time constraints.

- Prevent overlapping reservations.

- Store and retrieve booking confirmations.



Security responsibilities:



- Independently verify authorization.

- Enforce booking ownership.

- Enforce administrator permissions.

- Use parameterized SQL queries.

- Validate input before performing sensitive operations.

- Reject unauthorized internal service requests.



Only the Booking Service should access the SQLite database directly.



### Component 3: Confirmation Service



Responsibilities:



- Receive authorized confirmation generation jobs.

- Retrieve the booking associated with the authorized job.

- Generate confirmations using an installed Python helper package.

- Save confirmation results through the Booking Service.

- Return job completion information.



Security responsibilities:



- Verify authorization for each job.

- Process only the permitted booking.

- Use job scoped credentials when communicating with the Booking Service.

- Avoid unrestricted access to protected records.

- Operate without direct SQLite database access.



### External Dependency



The Confirmation Service uses a small, independently packaged Python helper package to format booking confirmations.



The package must be declared and installed as a dependency rather than copied directly into the Confirmation Service source code.



The build process must verify approved dependencies and reject unapproved or modified artifacts.



## 7. Data Flow and Trust Boundaries



The primary confirmation workflow involves all three application services.



1. Amin authenticates through the Application API.

2. Amin requests a booking confirmation for his own reservation.

3. The Application API verifies Amin's identity and authority.

4. The Application API issues limited authorization credentials.

5. The Application API sends an authorized confirmation job to the Confirmation Service.

6. The Confirmation Service requests the permitted booking from the Booking Service.

7. The Booking Service independently verifies the requested action, booking ownership, job authority, and credential validity.

8. The Booking Service returns the authorized booking information.

9. The Confirmation Service uses the external helper package to generate a confirmation.

10. The Confirmation Service stores the result through the Booking Service using scoped authorization.

11. Amin retrieves his confirmation through the Application API.



The following trust boundaries are identified:



- TB1: User to Application API

- TB2: Application API to Booking Service

- TB3: Application API to Confirmation Service

- TB4: Confirmation Service to Booking Service

- TB5: Confirmation Service to external helper package

- TB6: Booking Service to SQLite database



The system architecture and data flow diagrams are stored under docs/diagrams/.



## 8. Planned Security Vulnerability Investigations



The project will intentionally introduce and investigate four vulnerabilities.



Three vulnerabilities are selected from the course CWE vulnerability catalog.



The fourth vulnerability investigates a security weakness arising from composing independent application services.



### V1: CWE-862 Missing Authorization



Amin attempts to access a booking belonging to Casper by changing the requested booking identifier.



The vulnerable implementation does not verify ownership before returning the protected booking.



The secure implementation performs resource ownership validation in the Booking Service.



Expected security test:



Amin must not be able to retrieve Casper's private booking.



### V2: CWE-89 SQL Injection



Frank submits manipulated input through the room search functionality.



The vulnerable implementation constructs SQL statements using untrusted user input.



The secure implementation uses parameterized SQL queries.



Expected security test:



Manipulated search input must not alter the intended SQL query structure or allow unauthorized database operations.



### V3: CWE-20 Improper Input Validation



A user attempts to create a booking with an end time earlier than its start time.



The vulnerable implementation accepts invalid booking data.



The secure implementation validates booking time constraints before storing reservations.



Expected security test:



Bookings with invalid start and end times must be rejected.



### V4: Cross Service Authorization Bypass



The Confirmation Service attempts to retrieve a booking unrelated to its authorized confirmation job.



The vulnerable implementation grants excessive internal service authority.



The secure implementation uses credentials restricted to the intended service, booking, action, job, and validity period.



Expected security test:



The Confirmation Service must not retrieve unrelated booking records.



The legitimate confirmation workflow must continue to work after remediation.



### Additional Security Tests



The application will also test:



- Students cannot perform administrator only operations.

- Users cannot manipulate booking ownership fields.

- Missing or expired authorization credentials are rejected.

- Conflicting bookings are prevented.

- Unapproved dependency artifacts are rejected.



These additional tests support the overall security requirements without replacing the four selected vulnerability investigations.



## 9. Requirements Gate Review



The requirements phase is ready for approval when the following conditions are satisfied:



- Functional operations are documented.

- Non functional and security requirements are defined.

- The asset register identifies important protected resources.

- Three independent application services have distinct responsibilities.

- User identities, roles, and ownership rules are defined.

- The access control matrix documents permitted and forbidden operations.

- The STRIDE threat analysis identifies relevant threats and proposed controls.

- Architecture and data flow diagrams are available.

- The selected vulnerabilities match the course requirements.

- Planned security controls are connected to tests and evidence.

- The build and testing gates are defined.



**Gate Decision: APPROVED FOR IMPLEMENTATION**



The requirements gate is approved following a review of the initial plan, threat model, access control matrix, requirements, and architecture diagrams.



The project may now enter Phase 2: Implementation and Build. The planned security controls still require implementation and testing.



## 10. SSDLC Traceability and Evidence



The development process follows the required traceability structure:



Asset → Threat → Requirement or Control → Lifecycle Activity → Test or Evidence → Gate Decision



| Asset | Threat | Requirement or Control | Lifecycle Activity | Test or Evidence | Gate |

|---|---|---|---|---|---|

| Student bookings | CWE-862 Missing Authorization | Ownership validation | Implementation and testing | Cross user access test | Block on failure |

| SQLite data | CWE-89 SQL Injection | Parameterized SQL statements | Implementation and testing | SQL Injection regression test | Block on failure |

| Booking integrity | CWE-20 Improper Input Validation | Booking time validation | Implementation and testing | Invalid booking test | Block on failure |

| Service authority | Cross Service Authorization Bypass | Job scoped authorization | Architecture and testing | Unauthorized internal request test | Block on failure |

| Administrator operations | Unauthorized privilege use | Role verification | Implementation and testing | Student administrator access test | Block on failure |

| Helper dependency | Unapproved software artifact | Dependency integrity verification | Build and testing | Modified artifact rejection test | Block on failure |



Evidence will be preserved through:



- Git commits and relevant tags

- Architecture and data flow diagrams

- Functional and authorization tests

- Controlled vulnerability demonstrations

- Regression test reports

- Static analysis results

- Dependency analysis results

- Jenkins pipeline artifacts

- Screenshots of important implementation and security testing milestones
