# Test Cases

All 15 requirement specifications used as input to all systems. Requirements are provided exactly as written — informal, natural language descriptions typical of early-stage stakeholder communication.

## Class Diagram Test Cases

### TC01: Library: Library Management
**Complexity:** Simple (3 classes, 10 attributes, 2 relationships)

**Requirements:**
> So we need a system for our library. Basically there are books that members can borrow. Each book should have a title, the author name, ISBN and when it was published. For members we need to store their member ID, full name, email and phone. When someone borrows a book we need to track when they took it and when they returned it.

---

### TC02: Blog: Blog Platform
**Complexity:** Simple (3 classes, 8 attributes, 2 relationships)

**Requirements:**
> I want to build a simple blog where users can write posts. A user has a username, email and the date they signed up. Posts need a title, the actual content and when it was created. Each post is written by one user but users can write as many posts as they want. Also people should be able to leave comments on posts with some text and the date.

---

### TC03: Employee: Employee & Department
**Complexity:** Simple (2 classes, 6 attributes, 3 relationships)

**Requirements:**
> We have employees that work in different departments. For an employee we store their ID, name, when they were hired and their salary. Departments just have a name and location. Every employee belongs to one department and each department has multiple employees. Oh and one person in each department is the manager.

---

### TC04: ELearning: E-Learning Platform
**Complexity:** Complex (6 classes, 14 attributes, 7 relationships)

**Requirements:**
> Ok so this is for an online learning website. We have instructors who teach courses. Instructors have a name, email and their area of expertise. Courses have a title, description, price and difficulty level like beginner or advanced. Students can sign up for courses and we need to track their progress as a percentage. We also need to know when they enrolled. Each course is made up of lessons that have a title, the content, how long it takes and what order they come in. When students finish a lesson we record when they completed it.

---

### TC05: Hotel: Hotel Booking
**Complexity:** Medium (6 classes, 15 attributes, 5 relationships)

**Requirements:**
> This is for managing hotel bookings. The hotel has rooms and each room has a number, what type it is like single or double, which floor its on and the nightly rate. Guests have an ID, name, phone number and email. When someone makes a reservation we link them to a room and store check in date, check out date and total cost. We also need to handle payments that have the amount, date and how they paid like cash or credit card. One reservation might have multiple payments if they pay in installments. Rooms can also have amenities like wifi or a minibar.

---

### TC06: Restaurant: Restaurant Ordering
**Complexity:** Complex (8 classes, 13 attributes, 7 relationships)

**Requirements:**
> We need a system for restaurant orders. Theres a menu with items that have a name, description, price and what category they fall under. Categories are things like appetizers, main dishes, desserts and drinks. Customers come in and place orders which have multiple items in them. For each item in the order we need the menu item, how many they want and any special requests like no onions or extra sauce. Orders have an order number, when it was placed, the status and total. Waiters work at tables and take care of the orders. Tables have a number and how many people can sit there.

---

### TC07: ProjectTasks: Project Task Tracking
**Complexity:** Medium (4 classes, 13 attributes, 5 relationships)

**Requirements:**
> Building a tool to track project tasks. Projects have a name, description, when they started and the deadline. Tasks are part of projects and have a title, description, status, priority level and due date. Status is either todo, in progress, in review or done. We have team members with names and their role on the project. Members get assigned to tasks and they log their time. Time entries show how many hours they worked and what they did. Every project has one person whos the lead.

---

### TC08: OnlineStore: Online Store
**Complexity:** Complex (12 classes, 38 attributes, 15 relationships)

**Requirements:**
> Ok this is for an online store. Customers have an ID, first name, last name, email, phone, password and when they registered. Every customer gets a shopping cart and a wishlist. They can also save multiple shipping addresses with street, city, zip and country. The shopping cart has items in it. Each cart item points to a product and stores the quantity and when it was added. Products have an ID, name, description, price, how many are in stock and whether its active. Products belong to a category and can have multiple images with a URL and which one is the main image. Customers can leave reviews on products. Categories have an ID, name and description. They can be nested so a category might have a parent category and child categories underneath it. Reviews have an ID, a rating from 1 to 5, a comment and the date. Each review is written by a customer for a specific product. When someone checks out it creates an order with an ID, date, status and total. Status is pending, confirmed, shipped or delivered. Orders have line items with quantity and the price at the time of purchase. Orders get shipped to an address and have a payment record with ID, amount, method and date.

---

### TC09: Hospital: Hospital Management
**Complexity:** Complex (11 classes, 45 attributes, 11 relationships)

**Requirements:**
> This is for a hospital. We have patients with ID, first and last name, birthday, gender, blood type, phone and address. Doctors have an ID, name, what they specialize in, phone and email. Doctors are assigned to departments that have a name and what floor theyre on. Patients come in for appointments. Each appointment has an ID, the date and time, reason for visit and status which is scheduled, completed or cancelled. Appointments are always with one specific doctor. Doctors create medical records during appointments. Records have an ID, the diagnosis, symptoms, any notes and the date. Doctors can also write prescriptions with an ID, dosage instructions, start date and end date. Prescriptions are for medications that have an ID, name, who makes it and the price. Sometimes patients need to stay so we admit them to rooms. Rooms have a number, type like general or private, and daily rate. We track when they were admitted, discharged and the total cost. Patients get billed through invoices with a number, when it was issued, due date, total and whether its been paid. Invoices have line items for each service.

---

### TC10: University: University Registration
**Complexity:** Complex (9 classes, 29 attributes, 11 relationships)

**Requirements:**
> University registration system. Students have ID, first name, last name, email, when they enrolled and their GPA. Students pick a major that has a name and how many credits you need to graduate. Courses have a code like CS101, title, description and credit hours. Theyre offered by departments which have a name and building. Faculty teach the courses and have an ID, name, title like professor or assistant professor, and office location. Each semester there are sections of courses. Sections have a number, semester, year, when it meets and the room. Rooms have a number, building and how many seats. Faculty get assigned to teach sections and students enroll in them and get grades. We track what grade they got like A, B, C, D or F. Students can also join clubs that have a name and description. One student is the president of each club. Some courses have prerequisites that are other courses you need to take first. Courses can be required for a major or just electives.

---

## Use Case Diagram Test Cases

### TC11: ATM: ATM System
**Complexity:** Medium (3 actors, 9 use cases, 4 include relationships)

**Requirements:**
> We need to design an ATM. Bank customers should be able to check how much money they have, take out cash, put money in and move money between accounts. They have to enter their PIN first before doing anything. The bank system checks everything and updates the balances. Theres also admins who refill the cash and can look at the transaction history.

---

### TC12: OnlineStore: Online Store
**Complexity:** Medium (3 actors, 10 use cases, 1 include relationship)

**Requirements:**
> This is for an online store website. Customers can look at products, search by category, add stuff to their cart, checkout and see where their orders are. They need to log in before they can buy anything. Payments go through a third party payment system. Admin users manage whats in stock, handle refunds and pull up sales reports.

---

### TC13: Library: Library System
**Complexity:** Medium (2 actors, 9 use cases, 1 include relationship)

**Requirements:**
> Library system for members and librarians. Members can search for books, put books on hold, borrow them and bring them back. You have to be registered to borrow anything. Librarians add new books, get rid of old ones, manage member accounts and deal with late fees. The system also notifies people when a book they reserved is ready.

---

### TC14: Hospital: Hospital Appointment
**Complexity:** Complex (4 actors, 10 use cases, 2 include relationships)

**Requirements:**
> Hospital appointment booking with patients, doctors and front desk people. Patients can sign up, see what times are open, book an appointment and cancel if they need to. Doctors check their schedule and mark appointments as done. The receptionist handles the calendar, signs up walk-ins and sends reminders. It also connects to billing for payments.

---

### TC15: ELearning: E-Learning Platform
**Complexity:** Complex (3 actors, 13 use cases, 1 include relationship)

**Requirements:**
> Online learning site for students, teachers and admins. Students can look through courses, sign up for them, watch the videos, turn in homework and do quizzes. Teachers make the courses, upload stuff, grade work and post announcements. Admins handle user accounts, approve courses before they go live and keep track of whos using the platform. Students get a certificate when they finish a course.

---
