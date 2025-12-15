class JsonQuery {
  constructor(data) {
    this.data = Array.isArray(data) ? data : [data];
  }

  // Filter data based on a condition
  where(condition) {
    this.data = this.data.filter(condition);
    return this;
  }

  // Select specific fields
  select(fields) {
    this.data = this.data.map(item => {
      const result = {};
      fields.forEach(field => {
        result[field] = item[field];
      });
      return result;
    });
    return this;
  }

  // Order data by a field
  orderBy(field, direction = 'asc') {
    this.data.sort((a, b) => {
      if (a[field] < b[field]) return direction === 'asc' ? -1 : 1;
      if (a[field] > b[field]) return direction === 'asc' ? 1 : -1;
      return 0;
    });
    return this;
  }

  // Group data by a field
  groupBy(field) {
    const groups = {};
    this.data.forEach(item => {
      const key = item[field];
      if (!groups[key]) groups[key] = [];
      groups[key].push(item);
    });
    this.data = groups;
    return this;
  }

  // Limit the number of results
  limit(count) {
    this.data = this.data.slice(0, count);
    return this;
  }

  // Join with another dataset
  join(otherData, leftKey, rightKey) {
    this.data = this.data.map(leftItem => {
      const rightItem = otherData.find(rightItem => leftItem[leftKey] === rightItem[rightKey]);
      return { ...leftItem, ...rightItem };
    });
    return this;
  }

  // Count the number of items
  count() {
    return this.data.length;
  }

  // Sum a field
  sum(field) {
    return this.data.reduce((acc, item) => acc + item[field], 0);
  }

  // Calculate the average of a field
  avg(field) {
    return this.sum(field) / this.count();
  }

  // Get the result
  get() {
    return this.data;
  }
}

