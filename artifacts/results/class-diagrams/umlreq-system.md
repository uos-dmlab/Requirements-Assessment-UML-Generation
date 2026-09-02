# UMLReq System — Class Diagram Results

Generated using GPT-4o (gpt-4o-2024-11-20) via OpenAI API with temperature=0.3, top_p=1.0, RAG grounding in PlantUML documentation, and methodology-aware prompts (Larman's mapmaker principle).

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
memberId: int
fullName: String
email: String
phone: String
}

class Borrow {
borrowDate: Date
returnDate: Date
}

Member "1" -- "1..*" Borrow : borrows
Borrow "1" -- "1" Book : includes

@enduml
```

### Generated Diagram

![TC01_Library - UMLReq System](../images/class/umlreq/TC01_Library.png)

---

## TC02: Blog: Blog Platform

### PlantUML Code

```plantuml
@startuml

class User {
username: String
email: String
signUpDate: Date
}

class Post {
title: String
content: String
createdDate: Date
}

class Comment {
text: String
date: Date
}

User "1" -- "1..*" Post : writes
Post "1" o-- "*" Comment : has

@enduml
```

### Generated Diagram

![TC02_Blog - UMLReq System](../images/class/umlreq/TC02_Blog.png)

---

## TC03: Employee: Employee & Department

### PlantUML Code

```plantuml
@startuml

class Employee {
id: int
name: String
hiredDate: Date
salary: double
}

class Department {
name: String
location: String
}

Employee "1" --> "1" Department : belongs to
Department "1" o-- "*" Employee : has
Department "1" -- "1" Employee : manager

@enduml
```

### Generated Diagram

![TC03_Employee - UMLReq System](../images/class/umlreq/TC03_Employee.png)

---

## TC04: ELearning: E-Learning Platform

### PlantUML Code

```plantuml
@startuml

class Instructor {
name: String
email: String
areaOfExpertise: String
}

class Course {
title: String
description: String
price: double
difficultyLevel: String
}

class Student

class Progress {
percentage: double
enrolledDate: Date
}

class Lesson {
title: String
content: String
duration: int
order: int
}

class LessonCompletion {
completionDate: Date
}

Instructor "1" -- "1..*" Course : teaches
Student "1" -- "1..*" Course : enrolls in
Course "1" *-- "1..*" Lesson : contains
Student "1" -- "1..*" Progress : has
Progress "1" -- "1" Course : tracks
Student "1" -- "1..*" LessonCompletion : completes
LessonCompletion "1" -- "1" Lesson : records

@enduml
```

### Generated Diagram

![TC04_ELearning - UMLReq System](../images/class/umlreq/TC04_ELearning.png)

---

## TC05: Hotel: Hotel Booking

### PlantUML Code

```plantuml
@startuml

class Hotel

class Room {
number: int
type: String
floor: int
nightlyRate: double
}

class Guest {
id: int
name: String
phoneNumber: String
email: String
}

class Reservation {
checkInDate: Date
checkOutDate: Date
totalCost: double
}

class Payment {
amount: double
date: Date
paymentMethod: String
}

class Amenity {
name: String
}

Hotel "1" o-- "1..*" Room : has
Room "1" o-- "1..*" Amenity : has
Guest "1" -- "1..*" Reservation : makes
Reservation "1" -- "1" Room : links to
Reservation "1" o-- "0..*" Payment : has

@enduml
```

### Generated Diagram

![TC05_Hotel - UMLReq System](../images/class/umlreq/TC05_Hotel.png)

---

## TC06: Restaurant: Restaurant Ordering

### PlantUML Code

```plantuml
@startuml

class Menu

class MenuItem {
name: String
description: String
price: double
category: String
}

class Category {
name: String
}

class Order {
orderNumber: int
placedAt: Date
status: String
total: double
}

class OrderItem {
quantity: int
specialRequests: String
}

class Customer

class Waiter

class Table {
number: int
capacity: int
}

Menu "1" *-- "1..*" MenuItem : contains
MenuItem "1" -- "1" Category : belongs to
Order "1" *-- "1..*" OrderItem : contains
OrderItem "1" -- "1" MenuItem : references
Customer "1" -- "1..*" Order : places
Waiter "1" -- "1..*" Table : takes care of
Table "1" -- "1..*" Order : associated with

@enduml
```

### Generated Diagram

![TC06_Restaurant - UMLReq System](../images/class/umlreq/TC06_Restaurant.png)

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
status: String
priorityLevel: String
dueDate: Date
}

class TeamMember {
name: String
role: String
}

class TimeEntry {
hoursWorked: double
description: String
}

Project "1" *-- "1..*" Task : has
Task "1..1" -- "1..*" TeamMember : assigned to
TeamMember "1..*" o-- "1..*" TimeEntry : logs
Task "1..*" o-- "1..*" TimeEntry : has
Project "1" -- "1" TeamMember : lead by

@enduml
```

### Generated Diagram

![TC07_ProjectTasks - UMLReq System](../images/class/umlreq/TC07_ProjectTasks.png)

---

## TC08: OnlineStore: Online Store

### PlantUML Code

```plantuml
@startuml

class Customer {
id: int
firstName: String
lastName: String
email: String
phone: String
password: String
registeredDate: Date
}

class ShoppingCart

class Wishlist

class ShippingAddress {
street: String
city: String
zip: String
country: String
}

class CartItem {
quantity: int
addedDate: Date
}

class Product {
id: int
name: String
description: String
price: double
stock: int
isActive: boolean
}

class Category {
id: int
name: String
description: String
}

class Image {
url: String
isMain: boolean
}

class Review {
id: int
rating: int
comment: String
date: Date
}

class Order {
id: int
date: Date
status: String
total: double
}

class OrderItem {
quantity: int
priceAtPurchase: double
}

class Payment {
id: int
amount: double
method: String
date: Date
}

Customer "1" *-- "1" ShoppingCart : has
Customer "1" *-- "1" Wishlist : has
Customer "1" o-- "*" ShippingAddress : saves
ShoppingCart "1" *-- "*" CartItem : contains
CartItem "1" -- "1" Product : points to
Product "1" -- "1" Category : belongs to
Product "1" o-- "*" Image : has
Customer "1" -- "*" Review : writes
Review "1" -- "1" Product : for
Category "0..1" -- "*" Category : has parent
Customer "1" -- "*" Order : places
Order "1" *-- "*" OrderItem : contains
OrderItem "1" -- "1" Product : references
Order "1" -- "1" ShippingAddress : shipped to
Order "1" *-- "1" Payment : has

@enduml
```

### Generated Diagram

![TC08_OnlineStore - UMLReq System](../images/class/umlreq/TC08_OnlineStore.png)

---

## TC09: Hospital: Hospital Management

### PlantUML Code

```plantuml
@startuml

class Patient {
  id: int
  firstName: String
  lastName: String
  birthday: Date
  gender: String
  bloodType: String
  phone: String
  address: String
}

class Doctor {
  id: int
  name: String
  specialization: String
  phone: String
  email: String
}

class Department {
  name: String
  floor: int
}

class Appointment {
  id: int
  dateTime: DateTime
  reasonForVisit: String
  status: String
}

class MedicalRecord {
  id: int
  diagnosis: String
  symptoms: String
  notes: String
  date: Date
}

class Prescription {
  id: int
  dosageInstructions: String
  startDate: Date
  endDate: Date
}

class Medication {
  id: int
  name: String
  manufacturer: String
  price: double
}

class Room {
  number: int
  type: String
  dailyRate: double
}

class Admission {
  admittedDate: Date
  dischargedDate: Date
  totalCost: double
}

class Invoice {
  number: int
  issuedDate: Date
  dueDate: Date
  total: double
  isPaid: boolean
}

class LineItem {
  service: String
  cost: double
}

Doctor "1" -- "1" Department : assigned to
Patient "1" -- "1..*" Appointment : has
Doctor "1" -- "1..*" Appointment : conducts
Appointment "1" *-- "1..*" MedicalRecord : creates
Doctor "1" -- "1..*" MedicalRecord : writes
Doctor "1" -- "1..*" Prescription : writes
Prescription "1" -- "1" Medication : is for
Patient "0..1" -- "1" Room : admitted to
Room "1" *-- "1" Admission : tracks
Patient "1" -- "1..*" Invoice : billed through
Invoice "1" *-- "1..*" LineItem : contains

@enduml
```

### Generated Diagram

![TC09_Hospital - UMLReq System](../images/class/umlreq/TC09_Hospital.png)

---

## TC10: University: University Registration

### PlantUML Code

```plantuml
@startuml

class Student {
id: int
firstName: String
lastName: String
email: String
enrolledDate: Date
gpa: float
}

class Major {
name: String
requiredCredits: int
}

class Course {
code: String
title: String
description: String
creditHours: int
}

class Department {
name: String
building: String
}

class Faculty {
id: int
name: String
title: String
officeLocation: String
}

class Section {
number: int
semester: String
year: int
meetingTime: String
room: String
}

class Room {
number: String
building: String
seatCount: int
}

class Grade {
value: String
}

class Club {
name: String
description: String
}

Student "1" -- "1" Major : picks
Course "1" -- "1" Department : offered by
Faculty "1" -- "1..*" Section : teaches
Student "1" -- "1..*" Section : enrolls in
Section "1" -- "1" Room : meets in
Student "1" -- "1" Grade : receives
Section "1" -- "1..*" Grade : assigns
Student "1" -- "*" Club : joins
Club "1" -- "1" Student : has president
Course "1" -- "0..*" Course : has prerequisite
Course "1" -- "*" Major : required for

@enduml
```

### Generated Diagram

![TC10_University - UMLReq System](../images/class/umlreq/TC10_University.png)

---
