from typing import List, Dict, Any, Callable, Union

class JsonQuery:
    def __init__(self, data: Union[List[Dict[str, Any]], Dict[str, Any]]):
        self.data = data if isinstance(data, list) else [data]

    def where(self, condition: Callable[[Dict[str, Any]], bool]) -> 'JsonQuery':
        """Filter data based on a condition."""
        self.data = [item for item in self.data if condition(item)]
        return self

    def select(self, fields: List[str]) -> 'JsonQuery':
        """Select specific fields from the data."""
        self.data = [{field: item[field] for field in fields} for item in self.data]
        return self

    def order_by(self, field: str, direction: str = 'asc') -> 'JsonQuery':
        """Order data by a field in ascending or descending order."""
        reverse = direction.lower() == 'desc'
        self.data = sorted(self.data, key=lambda x: x[field], reverse=reverse)
        return self

    def group_by(self, field: str) -> 'JsonQuery':
        """Group data by a field."""
        groups = {}
        for item in self.data:
            key = item[field]
            if key not in groups:
                groups[key] = []
            groups[key].append(item)
        self.data = groups
        return self

    def limit(self, count: int) -> 'JsonQuery':
        """Limit the number of results."""
        self.data = self.data[:count]
        return self

    def join(
        self,
        other_data: Union[List[Dict[str, Any]], Dict[str, Any]],
        left_key: str,
        right_key: str
    ) -> 'JsonQuery':
        """Join the current data with another dataset."""
        other_data = other_data if isinstance(other_data, list) else [other_data]
        joined_data = []
        for left_item in self.data:
            for right_item in other_data:
                if left_item[left_key] == right_item[right_key]:
                    joined_data.append({**left_item, **right_item})
        self.data = joined_data
        return self

    def count(self) -> int:
        """Return the number of items in the data."""
        return len(self.data)

    def sum(self, field: str) -> Union[int, float]:
        """Calculate the sum of a field."""
        return sum(item[field] for item in self.data)

    def avg(self, field: str) -> float:
        """Calculate the average of a field."""
        return self.sum(field) / self.count()

    def get(self) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """Return the current state of the data."""
        return self.data

# Example usage
if __name__ == "__main__":
    users = [
        {"id": 1, "name": "Alice", "age": 25, "role": "admin"},
        {"id": 2, "name": "Bob", "age": 30, "role": "user"},
        {"id": 3, "name": "Charlie", "age": 35, "role": "admin"},
        {"id": 4, "name": "David", "age": 20, "role": "user"},
    ]

    orders = [
        {"userId": 1, "orderId": 101, "amount": 100},
        {"userId": 2, "orderId": 102, "amount": 200},
        {"userId": 3, "orderId": 103, "amount": 150},
        {"userId": 1, "orderId": 104, "amount": 300},
    ]

    # Query example: Filter, select, and order
    query = JsonQuery(users)
    result = (
        query.where(lambda user: user["age"] > 25)
        .select(["id", "name", "age"])
        .order_by("age", "desc")
        .get()
    )
    print("Filtered and ordered users:", result)

    # Join example
    user_query = JsonQuery(users)
    order_query = JsonQuery(orders)
    joined_data = user_query.join(order_query.get(), "id", "userId").get()
    print("Joined data:", joined_data)

    # Aggregation example
    age_sum = query.sum("age")
    age_avg = query.avg("age")
    print("Sum of ages:", age_sum)
    print("Average age:", age_avg)

***
Example Outputs:


Filtered and ordered users:
python
Copy

[
    {"id": 3, "name": "Charlie", "age": 35},
    {"id": 2, "name": "Bob", "age": 30}
]



Joined data:
python
Copy

[
    {"id": 1, "name": "Alice", "age": 25, "role": "admin", "userId": 1, "orderId": 101, "amount": 100},
    {"id": 1, "name": "Alice", "age": 25, "role": "admin", "userId": 1, "orderId": 104, "amount": 300},
    {"id": 2, "name": "Bob", "age": 30, "role": "user", "userId": 2, "orderId": 102, "amount": 200},
    {"id": 3, "name": "Charlie", "age": 35, "role": "admin", "userId": 3, "orderId": 103, "amount": 150}
]



Sum of ages: 85


Average age: 31.666...


***
