// Example usage:
const users = [
  { id: 1, name: "Alice", age: 25, role: "admin" },
  { id: 2, name: "Bob", age: 30, role: "user" },
  { id: 3, name: "Charlie", age: 35, role: "admin" },
  { id: 4, name: "David", age: 20, role: "user" },
];

const orders = [
  { userId: 1, orderId: 101, amount: 100 },
  { userId: 2, orderId: 102, amount: 200 },
  { userId: 3, orderId: 103, amount: 150 },
  { userId: 1, orderId: 104, amount: 300 },
];

// Query example:
const query = new JsonQuery(users);
const result = query
  .where(user => user.age > 25)
  .select(['id', 'name', 'age'])
  .orderBy('age', 'desc')
  .get();

console.log("Filtered and ordered users:", result);

// Join example:
const userQuery = new JsonQuery(users);
const orderQuery = new JsonQuery(orders);
const joinedData = userQuery
  .join(orderQuery.get(), 'id', 'userId')
  .get();

console.log("Joined data:", joinedData);

// Aggregation example:
const ageSum = query.sum('age');
const ageAvg = query.avg('age');
console.log("Sum of ages:", ageSum);
console.log("Average age:", ageAvg);
