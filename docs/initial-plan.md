\# Initial SSDLC Plan — Campus Room Booking System



\## 1. Project Overview



The Campus Room Booking System is a small Python application that allows university students to reserve study rooms, manage their own bookings, and generate booking confirmations.



The project's security objective is to protect individual users' bookings and investigate vulnerabilities that arise from authentication, authorization, and communication between independent application services.



\## 2. Users and Roles



The system will use four seeded accounts:



\- \*\*Amin:\*\* Student

\- \*\*Casper:\*\* Student

\- \*\*Frank:\*\* Student

\- \*\*Rasmus:\*\* Administrator



Students can manage their own bookings. The administrator can additionally manage room availability and view system-wide booking metadata.



An administrator does not automatically have permission to access every student's private booking confirmation.



\## 3. Functional Requirements



\- \*\*FR1:\*\* Users can log in using seeded accounts.

\- \*\*FR2:\*\* Users can view available study rooms.

\- \*\*FR3:\*\* Students can create room bookings.

\- \*\*FR4:\*\* Students can view and cancel their own bookings.

\- \*\*FR5:\*\* Students can generate and retrieve booking confirmations.

\- \*\*FR6:\*\* Administrators can manage room availability and view booking metadata.



The confirmation-generation functionality will involve all three application services.



\## 4. Non Functional and Security Requirements



\- The application must contain three independently running Python services communicating through HTTP.

\- Users must authenticate before performing protected operations.

\- Students must not access, modify, or cancel other students' bookings.

\- Room bookings must not overlap for the same room and time interval.

\- Administrative operations must require the administrator role.

\- Service-to-service requests must have limited and verifiable permissions.

\- Missing or invalid authorization must result in denied access.

\- Dependencies and build artifacts must be declared and approved.

\- Functional and security tests must execute automatically.

\- Jenkins must perform build verification, static analysis, dependency analysis, and automated testing.



\## 5. Application Architecture



The system consists of three services.



\### Component 1: Application API



Responsibilities:

\- Authenticate users.

\- Coordinate booking requests.

\- Establish user identity.

\- Issue limited authorization credentials for internal operations.



\### Component 2: Booking Service



Responsibilities:

\- Store rooms, bookings, and confirmation records.

\- Check room availability.

\- Create, retrieve, and cancel reservations.

\- Enforce resource ownership and administrator permissions.

\- Protect booking information requested by other services.



\### Component 3: Confirmation Service



Responsibilities:

\- Receive authorized confirmation-generation jobs.

\- Retrieve only the booking associated with an approved job.

\- Generate a booking confirmation.

\- Save the confirmation through the Booking Service.

\- Use an independently packaged Python helper dependency.



SQLite will provide persistent storage but will not count as one of the three application components.



The external helper package will format booking information into a confirmation document or text receipt. It will be packaged and installed as a separate Python dependency.



\## 6. Protected Assets and Trust Boundaries



Protected assets:

\- Student bookings

\- Booking confirmations

\- Room availability information

\- User credentials

\- Authentication and service authorization tokens

\- Approved dependency artifacts



Trust boundaries:

1\. User to Application API

2\. Application API to Booking Service

3\. Application API to Confirmation Service

4\. Confirmation Service to Booking Service

5\. Confirmation Service to external helper package



\## 7. Authorization Design



Students can create bookings, access their own reservations, cancel their own reservations, and generate confirmations for their own bookings.



The administrator can also manage rooms and access booking metadata for auditing.



Signed, time-limited credentials will be used to communicate authority. Internal authorization will be bound to the intended service, requested action, relevant booking or job, and validity period.



The Booking Service will independently verify permissions before allowing protected operations, including requests coming from the Confirmation Service.



\## 8. Secure Design Principles



\*\*Least Privilege:\*\* Each component receives only the permissions necessary to complete its responsibilities.



\*\*Complete Mediation:\*\* The Booking Service checks permissions whenever bookings or confirmations are accessed or modified.



\*\*Fail-Safe Defaults:\*\* Operations without valid authorization are denied by default.



These principles will be demonstrated through implementation decisions and automated security tests.



\## 9. Initial Security Traceability



| Asset | Threat | Control | Lifecycle Activity | Test/Evidence | Gate |

|---|---|---|---|---|---|

| Student bookings | Unauthorized access | Ownership validation | Implementation and testing | Amin cannot view Casper's booking | Block on failure |

| Administrator functions | Privilege escalation | Role validation | Implementation and testing | Frank cannot manage rooms | Block on failure |

| Booking ownership | Unauthorized ownership modification | Server-controlled owner | Implementation and testing | Forged owner rejected | Block on failure |

| Confirmation generation | Cross-service authorization bypass | Booking/job-scoped permissions | Design and testing | Confirmation Service cannot read unrelated bookings | Block on failure |

| Helper dependency | Modified or unapproved artifact | Artifact integrity verification | Build and testing | Unapproved package rejected | Block on failure |



\## 10. SSDLC Phases



\### Phase 1 Requirements



Activities:

\- Identify functional and non-functional requirements.

\- Define assets, users, roles, and operations.

\- Create architecture and data-flow diagrams.

\- Identify component trust boundaries.

\- Create an access-control matrix.

\- Perform STRIDE threat analysis.



\*\*Gate:\*\* Verify that the architecture satisfies the assignment requirements and that identified security threats have proposed controls.



\### Phase 2 Implementation and Build



Activities:

\- Implement the three Python application services.

\- Implement authentication and authorization.

\- Create SQLite-backed room and booking storage.

\- Build the installable confirmation helper package.

\- Configure Docker Compose.

\- Create reproducible builds and dependency checks.



\*\*Gate:\*\* Reject unexpected, modified, or unapproved dependencies and build artifacts.



\### Phase 3 Testing



Activities:

\- Write functional and authorization tests.

\- Investigate three vulnerabilities selected from the course catalog.

\- Investigate one additional vulnerability caused by composing application services.

\- Preserve evidence of vulnerable behavior.

\- Implement fixes and regression tests.

\- Configure Jenkins to run builds, security scans, and tests on pushes and pull requests.



\*\*Gate:\*\* All required functional and security tests must pass. Malformed or unapproved artifacts must be rejected. Blocking analysis findings must fail the pipeline.



\### Phase 4 Release, Deployment, and Operation



Activities:

\- Review application security.

\- Preserve Git history and test results.

\- Record Jenkins build and security analysis evidence.

\- Document requirements for a production release, including HTTPS, monitoring, backups, and secrets management.

\- Complete the written report and AI-use declaration.



\*\*Gate:\*\* Review the release candidate against the documented security requirements and test evidence.



\## 11. Planned Security Experiments



The project will investigate four candidate vulnerabilities:



1\. \*\*Insecure Direct Object Reference (IDOR):\*\* A student accesses another student's booking.

2\. \*\*Privilege Escalation:\*\* An ordinary student performs an administrator-only operation.

3\. \*\*Mass Assignment:\*\* A student attempts to create or modify a booking using another student's ownership identity.

4\. \*\*Cross-Service Authorization Bypass:\*\* The Confirmation Service attempts to retrieve a booking outside the authority of its assigned job.



The first three candidates must be checked against the course vulnerability catalog before implementation.



Each experiment will include a vulnerable implementation, a controlled demonstration, a remediation, and a regression test.



\## 12. Evidence Strategy



The repository will preserve:

\- Git commits and relevant tags

\- Architecture and trust-boundary diagrams

\- Access-control matrix and STRIDE analysis

\- Screenshots of important development milestones

\- Evidence of successful and blocked attacks

\- Automated functional and security test reports

\- Dependency and static analysis reports

\- Jenkins pipeline results

