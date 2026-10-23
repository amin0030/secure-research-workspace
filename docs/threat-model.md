# STRIDE Threat Model: Campus Room Booking System



## 1. Purpose



This document identifies potential security threats to the Campus Room Booking System using the STRIDE threat modelling methodology.



The purpose is to identify threats before implementation, define appropriate security controls, and establish tests that can demonstrate whether these controls work.



The threat model focuses on authentication, authorization, input validation, database operations, booking ownership, communication between services, and external dependencies.



The security investigations are based on three selected vulnerabilities from the course CWE catalog and one additional vulnerability caused by composing independent application services.



## 2. System Overview



The application consists of three independent Python services communicating through HTTP.



1. **Application API:** Authenticates users, checks roles, coordinates requests, and issues scoped authorization credentials.

2. **Booking Service:** Manages rooms, bookings, and confirmations, performs database operations, validates input, and enforces resource ownership.

3. **Confirmation Service:** Generates booking confirmations using an installed external Python helper package and accesses booking records only through authorized requests.



The application uses four seeded accounts:



- **Amin:** Student

- **Casper:** Student

- **Frank:** Student

- **Rasmus:** Administrator



Students can search for available rooms, create bookings, manage their own reservations, and generate booking confirmations.




The administrator can activate or deactivate existing rooms. The administrator cannot create student bookings or access private student bookings and confirmations. The current implementation does not provide system-wide booking metadata access.




Administrative privileges do not automatically grant access to other students' private booking information or confirmations.



SQLite provides persistent data storage but is not considered one of the three application components.



The external helper package is installed as a separate Python dependency used by the Confirmation Service.



## 3. Protected Assets



| Asset | Security Objective |

|---|---|

| Student bookings | Confidentiality and integrity |

| Booking confirmations | Confidentiality and integrity |

| Room availability | Integrity and availability |

| User credentials | Confidentiality |

| Authentication tokens | Confidentiality and integrity |

| Service authorization credentials | Confidentiality, integrity and limited authority |

| SQLite database | Confidentiality, integrity and availability |

| External Python helper package | Integrity |

| Security audit logs | Integrity and accountability |

| Test and CI evidence | Integrity and traceability |



Private booking information must only be accessible to users or services with the appropriate authority.



Room availability information must remain consistent to prevent conflicting reservations.



Authentication credentials, authorization tokens, and internal service permissions must be protected against unauthorized use.



## 4. Trust Boundaries



### TB1: Users to Application API



The Application API receives requests from students and administrators.



External input and user supplied information must not be automatically trusted.



Security responsibilities:



- Validate authentication credentials.

- Verify user identity and role.

- Validate incoming request data.

- Reject missing or invalid authentication.

- Prevent ordinary students from performing administrator operations.



### TB2: Application API to Booking Service



The Booking Service receives requests coordinated by the Application API.



Requests originating from the API are not automatically authorized.



Security responsibilities:



- Verify the authorization credentials.

- Verify the requested action and resource.

- Enforce booking ownership.

- Validate booking input and database operations.

- Enforce administrator permissions for restricted operations.



### TB3: Application API to Confirmation Service



The Confirmation Service receives requests to generate booking confirmations.



The service must verify that each job has the required authority.



Security responsibilities:



- Verify job authorization.

- Validate the booking identifier.

- Restrict processing to the authorized job.

- Reject requests with missing or invalid credentials.



### TB4: Confirmation Service to Booking Service



The Confirmation Service retrieves booking information and saves generated confirmations through the Booking Service.



The Booking Service must not assume that the Confirmation Service has unrestricted access to booking records.



Security responsibilities:



- Verify the intended booking and job.

- Verify the authorized action.

- Verify token audience and expiration.

- Enforce booking ownership.

- Reject access to unrelated bookings.



This trust boundary is central to the planned cross service authorization vulnerability investigation.



### TB5: Confirmation Service to External Python Package



The Confirmation Service executes an independently packaged Python helper dependency.



The package must not automatically be considered trustworthy merely because it is installed.



Security responsibilities:



- Verify approved dependency artifacts during installation.

- Restrict the Confirmation Service's runtime permissions.

- Avoid exposing database files or unrestricted service credentials.

- Limit the data passed to the helper package.



### TB6: Booking Service to SQLite Database



The Booking Service is responsible for database access.



Security responsibilities:



- Use parameterized SQL queries.

- Prevent unauthorized reading or modification of records.

- Enforce booking constraints.

- Prevent conflicting room reservations.

- Restrict direct database access to the Booking Service.



## 5. STRIDE Threat Analysis



STRIDE identifies six categories of security threats: Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, and Elevation of Privilege.



The following threats have been identified for the Campus Room Booking System.



| ID | STRIDE Category | Threat | Affected Boundary | Security Control | Planned Evidence |

|---|---|---|---|---|---|

| S1 | Spoofing | An attacker impersonates Amin using invalid or forged authentication credentials | TB1 | Password hashing, signed tokens and expiration verification | Invalid credentials and forged tokens are rejected |

| T1 | Tampering | SQL Injection through manipulated room search input affects database query behavior | TB1, TB2, TB6 | Parameterized SQL queries | Manipulated search input cannot alter SQL query structure |

| T2 | Tampering | A booking is created with invalid start and end times | TB1, TB2 | Input validation and booking constraints | Invalid booking times are rejected |

| T3 | Tampering | A user attempts to modify the owner of a booking | TB1, TB2 | Server controlled ownership | Forged ownership information is rejected |

| R1 | Repudiation | A user denies cancelling a booking | TB1, TB2 | Audit logging with authenticated identity and timestamps | Cancellation creates an audit record |

| I1 | Information Disclosure | Amin accesses a private booking belonging to Casper | TB2 | Booking ownership verification | Cross user access is denied |

| I2 | Information Disclosure | Confirmation Service accesses an unrelated private booking | TB4 | Booking and job scoped authorization | Unauthorized internal request is denied |

| D1 | Denial of Service | Oversized or repeated requests consume excessive resources | TB1 | Input size restrictions, timeouts and request limits | Oversized requests are rejected |

| E1 | Elevation of Privilege | Frank attempts to perform administrator operations | TB1, TB2 | Role based access control | Student receives HTTP 403 |

| E2 | Elevation of Privilege | Confirmation Service uses excessive internal permissions | TB4 | Limited service credentials and independent resource authorization | Unrelated booking request is rejected |

| T4 | Tampering | A modified or unapproved helper package is installed | TB5 | Artifact integrity verification | Modified dependency artifact is rejected |

| T5 | Tampering | Two overlapping reservations are accepted for the same room | TB6 | Transactional availability checking | Conflicting booking is rejected |



The identified threats will guide implementation decisions and security testing.



## 6. Risk Assessment



The following risk levels are initial qualitative estimates based on the potential likelihood and impact of each threat.



They will be reviewed during implementation and testing.



| Threat ID | Likelihood | Impact | Initial Priority |

|---|---|---|---|

| S1 | Medium | High | High |

| T1 | Medium | High | High |

| T2 | Medium | Medium | Medium |

| T3 | Medium | High | High |

| R1 | Medium | Medium | Medium |

| I1 | High | High | High |

| I2 | Medium | High | High |

| D1 | Medium | Medium | Medium |

| E1 | Medium | High | High |

| E2 | Medium | High | High |

| T4 | Medium | High | High |

| T5 | Medium | Medium | Medium |



Unauthorized access to student bookings and excessive internal service privileges are considered high priority because they can expose protected resources belonging to different users.



SQL Injection is also considered high priority because it can compromise the confidentiality or integrity of data stored in SQLite.



Improper Input Validation can affect the correctness and consistency of room reservations.



## 7. Planned Vulnerability Investigations



The project will intentionally introduce and investigate four vulnerabilities.



The first three are selected from the course CWE vulnerability catalog.



The fourth vulnerability specifically investigates a security failure caused by composing independent application services.



### V1: CWE-862 Missing Authorization



**Vulnerability description:**



Amin attempts to retrieve a private booking belonging to Casper by modifying the requested booking identifier.



The vulnerable Booking Service retrieves and returns the booking without verifying whether Amin owns it.



**Security assumption violated:**



An authenticated user is assumed to be authorized to access the requested resource.



**Underlying factor:**



Missing resource ownership validation.



**Potential impact:**



Unauthorized disclosure of another student's booking information.



**Security control:**



The Booking Service verifies the authenticated user and the ownership of every protected booking.



**Planned test:**



Amin attempts to access Casper's booking.



The vulnerable implementation exposes the booking.



The secure implementation denies the request with HTTP 403 or 404.



### V2: CWE-89 SQL Injection



**Vulnerability description:**



Frank submits manipulated input through the room search functionality.



The vulnerable Booking Service constructs an SQL statement by combining untrusted search input directly with SQL syntax.



**Security assumption violated:**



User controlled input is assumed to remain ordinary data when included in a database query.



**Underlying factor:**



SQL statement construction without parameterized queries.



**Potential impact:**



An attacker may influence database queries and potentially access or modify information outside the intended search functionality.



**Security control:**



The Booking Service uses parameterized SQL statements so that user supplied values remain data rather than executable SQL syntax.



**Planned test:**



A controlled SQL Injection test is performed against the vulnerable room search endpoint using synthetic data.



The vulnerable implementation demonstrates altered SQL query behavior.



The corrected implementation processes the same input as data without changing the intended query structure.



### V3: CWE-20 Improper Input Validation



**Vulnerability description:**



A user attempts to create a booking with an end time earlier than its start time.



The vulnerable Booking Service accepts the request without verifying the booking time constraints.



**Security assumption violated:**



User supplied booking information is assumed to satisfy the required constraints.



**Underlying factor:**



Insufficient validation of input values and booking semantics.



**Potential impact:**



Invalid reservations can be stored, affecting data integrity and room availability.



**Security control:**



The Booking Service validates booking times before database operations.



The start time must be earlier than the end time.



**Planned test:**



A booking request is submitted with invalid start and end times.



The vulnerable implementation accepts the booking.



The corrected implementation rejects the request with a validation error.



### V4: Cross Service Authorization Bypass



**Vulnerability description:**



The Confirmation Service receives permission to generate a confirmation for one specific booking.



The vulnerable implementation gives the Confirmation Service excessive internal permissions, allowing it to request an unrelated booking from the Booking Service.



**Security assumption violated:**



A trusted internal service is assumed to be authorized to access any booking required by its requests.



**Underlying factor:**



Excessive service privileges and missing authorization enforcement across component boundaries.



**Potential impact:**



The Confirmation Service can access private booking information outside the authority of its assigned job.



**Security control:**



The Application API issues credentials restricted to the intended service, booking, action, job, and validity period.



The Booking Service independently validates this authority before returning or modifying records.



**Planned test:**



The Confirmation Service is authorized to process Amin's booking.



During the controlled experiment, it attempts to retrieve Casper's booking.



The vulnerable implementation allows the unauthorized access.



The corrected implementation rejects the unrelated request while still allowing the legitimate confirmation job to complete.



### Experiment and Evidence Strategy



Each vulnerability investigation will include:



1. An intentionally vulnerable implementation.

2. A controlled demonstration using synthetic data.

3. Evidence of the violated security assumption.

4. A documented remediation.

5. A regression test demonstrating that the vulnerability is mitigated.



The vulnerable and corrected versions will be preserved through Git commits and relevant tags.



Experiments will run only in an isolated local test environment.



The final implementation must enforce the documented security requirements.



## 8. Secure Design Principles



### Least Privilege



Each user and component receives only the authority necessary to perform its intended operations.



The Confirmation Service must not have unrestricted database access or unrestricted permission to retrieve all bookings.



**Planned evidence:**



A cross service authorization test verifies that Confirmation Service cannot access an unrelated booking.



### Complete Mediation



Every protected booking operation requires authorization verification.



The Booking Service enforces permissions for requests from both the Application API and the Confirmation Service.



**Planned evidence:**



Authorization tests demonstrate that unauthorized booking access is rejected regardless of which service initiates the request.



### Fail Safe Defaults



Operations must be rejected when authentication, authorization, or required input validation is missing or invalid.



Unapproved dependencies must also be rejected during build verification.



**Planned evidence:**



Tests verify that missing tokens, expired credentials, invalid booking data, and unauthorized dependency artifacts are rejected.



## 9. Security Testing Strategy



Security testing will include:



- Authentication tests using valid and invalid credentials.

- Verification of signed token validity and expiration.

- Resource ownership tests between Amin, Casper, and Frank.

- Administrator authorization tests using Rasmus and ordinary student accounts.

- CWE-862 Missing Authorization vulnerability demonstrations and regression tests.

- CWE-89 SQL Injection vulnerability demonstrations and regression tests.

- CWE-20 Improper Input Validation demonstrations and regression tests.

- Cross Service Authorization Bypass demonstrations and regression tests.

- Tests verifying that booking ownership cannot be manipulated.

- Tests preventing overlapping room bookings.

- Dependency integrity verification.

- Functional tests demonstrating successful confirmation generation through all three services.

- Logging tests verifying that security relevant operations are recorded without exposing credentials.




Security tests are automated using Python unittest, including API integration tests, authorization regression tests, and helper package integrity tests.




Static analysis, dependency analysis, and functional and authorization tests will be integrated into the Jenkins pipeline.



## 10. SSDLC Gate Decisions



### Requirements Gate



The system architecture, requirements, assets, trust boundaries, user roles, permissions, and relevant security threats must be documented before implementation.



### Implementation and Build Gate



All three services must build successfully.



Dependencies must be declared and approved.



Modified, unexpected, or unapproved dependency artifacts must be rejected.



### Testing Gate



All required functional and security tests must pass.



Confirmed authorization violations must be corrected.



The three selected CWE vulnerabilities and the additional composition vulnerability must be demonstrated, documented, and mitigated.



Malformed or unauthorized inputs must be rejected.



### Release Gate



The final implementation must satisfy the documented security requirements.



Git history, vulnerability evidence, test results, static analysis, dependency analysis, and Jenkins pipeline results must be reviewed.



Production deployment requirements must be discussed in the final report.



## 11. Evidence Collection



The following evidence will be collected during implementation and testing:



- Git commits and relevant tags

- Architecture and data flow diagrams

- Access Control Matrix

- STRIDE Threat Model

- Security test results

- Screenshots of controlled vulnerability demonstrations

- Logs of rejected unauthorized requests

- Functional test results

- Static analysis reports

- Dependency analysis reports

- Jenkins pipeline results
