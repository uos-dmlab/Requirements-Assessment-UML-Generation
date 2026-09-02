# ChatGPT PlantUML — Class Diagram Results

Generated using ChatGPT web interface (chatgpt.com) with GPT-5.2 Thinking, prompted: "Generate PlantUML code for a class diagram based on these requirements. Return only the code between @startuml and @enduml." Code was then rendered via plantuml.com.

## TC01: Library: Library Management

### PlantUML Code

```plantuml
@startuml
class Book {

title: String

authorName: String

isbn: String

publishedDate: Date
}

class Member {

memberId: String

fullName: String

email: String

phone: String
}

class Borrowing {

borrowedAt: Date

returnedAt: Date
}

Member "1" -- "0.." Borrowing : makes
Book "1" -- "0.." Borrowing : is borrowed in
@enduml
```

### Generated Diagram

![TC01_Library - ChatGPT PlantUML](../images/class/chatgpt/TC01_Library.png)

---

## TC02: Blog: Blog Platform

### PlantUML Code

```plantuml
@startuml
class User {

username: String

email: String

signedUpAt: Date
}

class Post {

title: String

content: String

createdAt: Date
}

class Comment {

text: String

createdAt: Date
}

User "1" -- "0.." Post : writes
Post "1" -- "0.." Comment : has
@enduml
```

### Generated Diagram

![TC02_Blog - ChatGPT PlantUML](../images/class/chatgpt/TC02_Blog.png)

---

## TC03: Employee: Employee & Department

### PlantUML Code

```plantuml
@startuml
class Employee {

employeeId: String

name: String

hiredAt: Date

salary: Decimal
}

class Department {

name: String

location: String
}

Department "1" -- "1..*" Employee : has employees
Employee "1" --> "1" Department : belongs to
Department "1" --> "1" Employee : manager
@enduml
```

### Generated Diagram

![TC03_Employee - ChatGPT PlantUML](../images/class/chatgpt/TC03_Employee.png)

---

## TC04: ELearning: E-Learning Platform

### PlantUML Code

```plantuml
@startuml
class Instructor {

name: String

email: String

expertiseArea: String
}

class Course {

title: String

description: String

price: Decimal

difficultyLevel: String
}

class Student {

name: String

email: String
}

class Enrollment {

enrolledAt: Date

progressPercent: Integer
}

class Lesson {

title: String

content: String

durationMinutes: Integer

orderIndex: Integer
}

class LessonCompletion {

completedAt: Date
}

Instructor "1" -- "0.." Course : teaches
Course "1" -- "1.." Lesson : contains
Student "1" -- "0.." Enrollment : enrolls in
Course "1" -- "0.." Enrollment : has enrollments
Student "1" -- "0.." LessonCompletion : completes
Lesson "1" -- "0.." LessonCompletion : completion records
@enduml
```

### Generated Diagram

![TC04_ELearning - ChatGPT PlantUML](../images/class/chatgpt/TC04_ELearning.png)

---

## TC05: Hotel: Hotel Booking

### PlantUML Code

```plantuml
@startuml
class Room {

roomNumber: String

roomType: String

floor: Integer

nightlyRate: Decimal
}

class Guest {

guestId: String

name: String

phoneNumber: String

email: String
}

class Reservation {

checkInDate: Date

checkOutDate: Date

totalCost: Decimal
}

class Payment {

amount: Decimal

paymentDate: Date

paymentMethod: String
}

class Amenity {

name: String
}

Guest "1" -- "0.." Reservation : makes
Room "1" -- "0.." Reservation : booked for
Reservation "1" -- "0.." Payment : has payments
Room "0.." -- "0..*" Amenity : has
@enduml
```

### Generated Diagram

![TC05_Hotel - ChatGPT PlantUML](../images/class/chatgpt/TC05_Hotel.png)

---

## TC06: Restaurant: Restaurant Ordering

### PlantUML Code

```plantuml
@startuml
class MenuItem {

name: String

description: String

price: Decimal
}

class Category {

name: String
}

class Customer {

customerId: String

name: String
}

class Order {

orderNumber: String

placedAt: DateTime

status: String

total: Decimal
}

class OrderItem {

quantity: Integer

specialRequests: String
}

class Waiter {

waiterId: String

name: String
}

class RestaurantTable {

tableNumber: String

capacity: Integer
}

Category "1" -- "0.." MenuItem : contains
Customer "1" -- "0.." Order : places
Order "1" -- "1.." OrderItem : includes
MenuItem "1" -- "0.." OrderItem : ordered as
Waiter "1" -- "0.." Order : takes
RestaurantTable "1" -- "0.." Order : for
Waiter "1" -- "0..*" RestaurantTable : serves
@enduml
```

### Generated Diagram

![TC06_Restaurant - ChatGPT PlantUML](../images/class/chatgpt/TC06_Restaurant.png)

---

## TC07: ProjectTasks: Project Task Tracking

### PlantUML Code

```plantuml
@startuml
class Project {

name: String

description: String

startDate: Date

deadline: Date
}

class Task {

title: String

description: String

status: TaskStatus

priorityLevel: String

dueDate: Date
}

class TeamMember {

name: String

role: String
}

class TimeEntry {

hoursWorked: Decimal

workDescription: String
}

enum TaskStatus {
TODO
IN_PROGRESS
IN_REVIEW
DONE
}

Project "1" -- "1.." Task : contains
Project "1" --> "1" TeamMember : lead
TeamMember "0.." -- "0.." Task : assigned to
Task "1" -- "0.." TimeEntry : has time entries
TeamMember "1" -- "0..*" TimeEntry : logs
@enduml
```

### Generated Diagram

![TC07_ProjectTasks - ChatGPT PlantUML](../images/class/chatgpt/TC07_ProjectTasks.png)

---

## TC08: OnlineStore: Online Store

### PlantUML Code

```plantuml
@startuml
class Customer {

customerId: String

firstName: String

lastName: String

email: String

phone: String

password: String

registeredAt: DateTime
}

class ShoppingCart {

cartId: String

createdAt: DateTime
}

class Wishlist {

wishlistId: String

createdAt: DateTime
}

class Address {

addressId: String

street: String

city: String

zip: String

country: String
}

class CartItem {

quantity: Integer

addedAt: DateTime
}

class Product {

productId: String

name: String

description: String

price: Decimal

stockQuantity: Integer

isActive: Boolean
}

class ProductImage {

imageUrl: String

isMainImage: Boolean
}

class Category {

categoryId: String

name: String

description: String
}

class Review {

reviewId: String

rating: Integer

comment: String

reviewDate: DateTime
}

class Order {

orderId: String

orderDate: DateTime

status: OrderStatus

total: Decimal
}

class OrderLineItem {

quantity: Integer

purchasePrice: Decimal
}

class Payment {

paymentId: String

amount: Decimal

method: String

paymentDate: DateTime
}

enum OrderStatus {
PENDING
CONFIRMED
SHIPPED
DELIVERED
}

Customer "1" -- "1" ShoppingCart : has
Customer "1" -- "1" Wishlist : has
Customer "1" -- "0.." Address : saves
ShoppingCart "1" -- "0.." CartItem : contains
CartItem "1" --> "1" Product : product

Category "0..1" <-- "0.." Category : parent
Category "1" -- "0.." Product : contains
Product "1" -- "0..*" ProductImage : has images

Customer "1" -- "0.." Review : writes
Product "1" -- "0.." Review : receives

Customer "1" -- "0.." Order : places
Order "1" -- "1.." OrderLineItem : contains
OrderLineItem "1" --> "1" Product : product
Order "1" --> "1" Address : ships to
Order "1" -- "1" Payment : payment record
@enduml
```

### Generated Diagram

![TC08_OnlineStore - ChatGPT PlantUML](../images/class/chatgpt/TC08_OnlineStore.png)

---

## TC09: Hospital: Hospital Management

### PlantUML Code

```plantuml
@startuml
class Patient {

patientId: String

firstName: String

lastName: String

birthDate: Date

gender: String

bloodType: String

phone: String

address: String
}

class Doctor {

doctorId: String

name: String

specialization: String

phone: String

email: String
}

class Department {

name: String

floor: Integer
}

class Appointment {

appointmentId: String

appointmentDateTime: DateTime

reasonForVisit: String

status: AppointmentStatus
}

class MedicalRecord {

recordId: String

diagnosis: String

symptoms: String

notes: String

recordDate: Date
}

class Prescription {

prescriptionId: String

dosageInstructions: String

startDate: Date

endDate: Date
}

class Medication {

medicationId: String

name: String

manufacturer: String

price: Decimal
}

class Room {

roomNumber: String

roomType: String

dailyRate: Decimal
}

class Admission {

admittedAt: DateTime

dischargedAt: DateTime

totalCost: Decimal
}

class Invoice {

invoiceNumber: String

issuedDate: Date

dueDate: Date

total: Decimal

paid: Boolean
}

class InvoiceLineItem {

description: String

amount: Decimal
}

enum AppointmentStatus {
SCHEDULED
COMPLETED
CANCELLED
}

Department "1" -- "0.." Doctor : assigns
Patient "1" -- "0.." Appointment : has
Doctor "1" -- "0..*" Appointment : attends

Appointment "1" -- "0..1" MedicalRecord : creates
Doctor "1" -- "0.." MedicalRecord : writes
Patient "1" -- "0.." MedicalRecord : has

Doctor "1" -- "0.." Prescription : writes
Patient "1" -- "0.." Prescription : receives
Medication "1" -- "0..*" Prescription : prescribed medication

Patient "1" -- "0.." Admission : admitted
Room "1" -- "0.." Admission : stays in

Patient "1" -- "0.." Invoice : billed by
Invoice "1" -- "1.." InvoiceLineItem : contains
@enduml
```

### Generated Diagram

![TC09_Hospital - ChatGPT PlantUML](../images/class/chatgpt/TC09_Hospital.png)

---

## TC10: University: University Registration

### PlantUML Code

```plantuml
@startuml
class Student {

studentId: String

firstName: String

lastName: String

email: String

enrolledAt: Date

gpa: Decimal
}

class Major {

name: String

creditsRequiredToGraduate: Integer
}

class Course {

courseCode: String

title: String

description: String

creditHours: Integer
}

class Department {

name: String

building: String
}

class Faculty {

facultyId: String

name: String

title: String

officeLocation: String
}

class Section {

sectionNumber: String

semester: String

year: Integer

meetingTime: String

room: String
}

class Room {

roomNumber: String

building: String

seatCapacity: Integer
}

class Enrollment {

grade: Grade
}

class Club {

name: String

description: String
}

class ClubMembership {

joinedAt: Date
}

class MajorCourseRequirement {

requirementType: RequirementType
}

enum Grade {
A
B
C
D
F
}

enum RequirementType {
REQUIRED
ELECTIVE
}

Major "1" -- "0.." Student : chosen by
Department "1" -- "0.." Course : offers
Department "1" -- "0..*" Faculty : has

Course "1" -- "0.." Section : has sections
Faculty "1" -- "0.." Section : teaches
Room "1" -- "0..*" Section : hosts

Student "1" -- "0.." Enrollment : enrolls in
Section "1" -- "0.." Enrollment : has enrollments

Student "1" -- "0.." ClubMembership : joins
Club "1" -- "0.." ClubMembership : has members
Club "1" --> "1" Student : president

Course "0.." --> "0.." Course : prerequisite
Major "1" -- "0.." MajorCourseRequirement : curriculum
Course "1" -- "0.." MajorCourseRequirement : counts for
@enduml
```

### Generated Diagram

![TC10_University - ChatGPT PlantUML](../images/class/chatgpt/TC10_University.png)

---
