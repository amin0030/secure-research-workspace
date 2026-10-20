# Initial SSDLC Plan: Campus Room Booking System



## 1. Project Overview



The Campus Room Booking System is a small Python application that allows university students to search for available study rooms, create and manage reservations, and generate booking confirmations.



The project's security objective is to protect individual users' bookings and investigate vulnerabilities arising from authentication, authorization, input validation, database operations, and communication between independent application services.



The application will be developed using a Secure Software Development Life Cycle (SSDLC) approach, with security requirements, threat modelling, testing, and release gates integrated into development.



## 2. Users and Roles



The system will use four seeded accounts:



* **Amin:** Student
* **Casper:** Student
* **Frank:** Student
* **Rasmus:** Administrator



Students can search for rooms, create bookings, manage their own reservations, and generate booking confirmations.



The administrator can additionally manage rooms and view system-wide booking metadata.



An administrator does not automatically have permission to access every student's private booking details or confirmations.



## 3. Functional Requirements



* **FR1:** Users can log in using seeded accounts.
* **FR2:** Users can view and search available study rooms.
* **FR3:** Students can create room bookings.
* **FR4:** Students can view and cancel their own bookings.
* **FR5:** Students can generate and retrieve booking confirmations.
* **FR6:** Administrators can manage room availability and view booking metadata.



The confirmation generation functionality will involve all three application services.



## 4. Non Functional and Security Requirements



* The application must contain three independently running Python services communicating through HTTP.
* Users must authenticate before performing protected operations.
* Students must not access, modify, or cancel other students' bookings.
* Room bookings must not overlap for the same room and time interval.
* Administrative operations must require the administrator role.
* Service to service requests must have limited and verifiable permissions.
* Missing or invalid authorization must result in denied access.
* Database queries must use parameterized SQL statements.
* User input must be validated before being used in security sensitive operations.
* Booking start times must be earlier than booking end times.
* Dependencies and build artifacts must be declared and approved.
* Functional and security tests must execute automatically.
* Jenkins must perform build verification, static analysis, dependency analysis, and automated testing.



## 5. Application Architecture



The system consists of three independent Python services.



### Component 1: Application API



Responsibilities:



* Authenticate users.
* Coordinate booking and confirmation requests.
* Establish user identity and roles.
* Issue limited authorization credentials for internal operations.
* Forward authorized requests to the relevant services.



### Component 2: Booking Service



Responsibilities:



* Store rooms, bookings, and confirmation records.
* Allow users to search for available study rooms.
* Check room availability.
* Create, retrieve, and cancel reservations.
* Validate booking data and prevent overlapping reservations.
* Use parameterized SQL queries to interact with SQLite.
* Enforce resource ownership and administrator permissions.
* Protect booking information requested by other services.



### Component 3: Confirmation Service



Responsibilities:



* Receive authorized confirmation generation jobs.
* Retrieve only the booking associated with an approved job.
* Generate a booking confirmation.
* Save the confirmation through the Booking Service.
* Use an independently packaged Python helper dependency.



SQLite will provide persistent storage but will not count as one of the three application components.



The external helper package will format booking information into a confirmation document or text receipt. It will be packaged and installed as a separate Python dependency.



## 6. Protected Assets and Trust Boundaries



Protected assets:



* Student bookings
* Booking confirmations
* Room availability information
* User credentials
* Authentication and service authorization tokens
* SQLite database records
* Approved dependency artifacts
* Security logs and test evidence



Trust boundaries:



1. User to Application API
2. Application API to Booking Service
3. Application API to Confirmation Service
4. Confirmation Service to Booking Service
5. Confirmation Service to external helper package
6. Booking Service to SQLite database



Each trust boundary represents a point where data or authority crosses between components with different responsibilities and permissions.



## 7. Authorization Design



Students can create bookings, access their own reservations, cancel their own reservations, and generate confirmations for their own bookings.



The administrator can additionally manage rooms and access booking metadata for auditing.



Signed, time limited credentials will be used to communicate authority between services.



Internal authorization will be bound to:



* The intended receiving service
* The authenticated user
* The requested action
* The relevant booking or job
* The validity period



The Booking Service will independently verify permissions before allowing protected operations, including requests originating from the Confirmation Service.



The Confirmation Service must not receive unrestricted access to all bookings.



The Booking Service must verify that the requested resource and action match the authority provided by the request.



## 8. Secure Design Principles



### Least Privilege



Each component receives only the permissions necessary to complete its responsibilities.



The Confirmation Service must only access bookings associated with its authorized confirmation jobs.



### Complete Mediation



The Booking Service validates authorization for every protected resource operation, including requests received from other services.



### Fail Safe Defaults



Operations without valid authentication or authorization are denied by default.



Invalid booking data and unauthorized requests must be rejected rather than processed.



These three principles will be demonstrated through implementation decisions and automated security tests.



## 9. Initial Security Traceability



The project follows this security traceability approach:



Asset → Threat → Requirement or Control → Lifecycle Activity → Test or Evidence → Gate Decision



| Asset | Threat | Control | Lifecycle Activity | Test or Evidence | Gate |

|---|---|---|---|---|---|

| Student bookings | CWE-862 Missing Authorization | Resource ownership validation | Implementation and testing | Amin cannot access Casper's booking | Block on failure |

| Room search | CWE-89 SQL Injection | Parameterized SQL queries | Implementation and testing | Manipulated input cannot change SQL query behavior | Block on failure |

| Booking data | CWE-20 Improper Input Validation | Booking time and input validation | Implementation and testing | Invalid booking times are rejected | Block on failure |

| Confirmation generation | Cross Service Authorization Bypass | Job scoped authorization | Architecture and testing | Confirmation Service cannot access unrelated bookings | Block on failure |

| Administrator functions | Unauthorized privileged operations | Role based authorization | Implementation and testing | Frank cannot manage rooms | Block on failure |

| Booking ownership | Unauthorized ownership modification | Server controlled ownership | Implementation and testing | Forged ownership is rejected | Block on failure |

| External dependency | Unapproved or modified package | Dependency integrity verification | Build and testing | Modified package is rejected | Block on failure |



## 10. SSDLC Phases



### Phase 1: Requirements



Activities:



* Identify functional and non functional requirements.
* Define users, roles, resources, and permitted operations.
* Create an architecture diagram and data flow diagram.
* Identify component trust boundaries.
* Create an access control matrix.
* Perform STRIDE threat analysis.
* Create an asset register.
* Select security vulnerabilities from the course CWE catalog.



**Gate:** Verify that the architecture satisfies the assignment requirements and that identified security threats have proposed controls.



### Phase 2: Implementation and Build



Activities:



* Implement three independently running Python services.
* Implement authentication and authorization.
* Create SQLite backed room and booking storage.
* Implement room searching and booking validation.
* Use parameterized SQL queries.
* Build the installable confirmation helper package.
* Configure Docker Compose.
* Create reproducible builds and dependency checks.



**Gate:** Unexpected, modified, or unapproved dependencies and build artifacts must be rejected.



### Phase 3: Testing



Activities:



* Implement functional and authorization tests.
* Investigate three vulnerabilities selected from the course CWE catalog.
* Investigate one additional vulnerability caused by composing application services.
* Preserve evidence of vulnerable behavior.
* Implement security fixes and regression tests.
* Configure Jenkins to run builds, security scans, and automated tests on pushes and pull requests.



**Gate:** All required functional and security tests must pass. Malformed and unapproved artifacts must be rejected. Blocking security findings must fail the pipeline.



### Phase 4: Release, Deployment, and Operation



Activities:



* Review application security and implemented controls.
* Preserve Git history and test results.
* Record Jenkins build and security analysis evidence.
* Document production requirements such as HTTPS, monitoring, backups, and secret management.
* Complete the written report and AI use declaration.



**Gate:** Review the release candidate against the documented security requirements and test evidence.



## 11. Planned Security Experiments



The project will investigate four intentionally introduced vulnerabilities.



### V1: CWE-862 Missing Authorization



Amin attempts to access a private booking belonging to Casper by changing the booking identifier.



The vulnerable implementation fails to verify booking ownership.



The secure implementation enforces ownership checks in the Booking Service.



### V2: CWE-89 SQL Injection



Frank submits manipulated input through the room search functionality.



The vulnerable implementation constructs SQL statements by combining SQL syntax with untrusted user input.



The secure implementation uses parameterized SQL queries to ensure that user input is treated as data rather than executable SQL syntax.



### V3: CWE-20 Improper Input Validation



A user attempts to create a booking with an end time earlier than its start time.



The vulnerable implementation accepts invalid booking data.



The secure implementation validates booking time constraints before storing the reservation.



### V4: Cross Service Authorization Bypass



The Confirmation Service attempts to access a booking unrelated to its authorized confirmation job.



The vulnerable implementation gives the Confirmation Service excessively broad permissions when communicating with the Booking Service.



The secure implementation uses credentials restricted to the intended booking, action, receiving service, job, and validity period.



This experiment specifically investigates a vulnerability arising from the composition of separate services and the incorrect transfer of authority across service boundaries.



### Experiment and Evidence Strategy



The first three vulnerabilities are selected from the course CWE vulnerability catalog.



The fourth vulnerability specifically investigates authorization failures caused by composing independent application services.



Each investigation will include:



1. An intentionally vulnerable implementation.
2. A controlled demonstration using synthetic data.
3. Evidence of the security violation.
4. A documented security fix.
5. A regression test demonstrating that the vulnerability is mitigated.



The vulnerable and corrected implementations will be preserved through Git history and documented in the final report.



All vulnerability experiments will be conducted in a controlled local environment.



## 12. Evidence Strategy



The repository will preserve:



* Git commits and relevant tags
* Architecture and trust boundary diagrams
* Access control matrix and STRIDE threat analysis
* Screenshots of important development milestones
* Evidence of successful and blocked attacks
* Automated functional and security test reports
* Dependency and static analysis reports
* Jenkins pipeline results
* Documentation of security decisions and fixes
