# API Design for the backend

## POST `/`

### Description



### Parameters

| Parameter | Required | Type                                  | default |
| --------- | -------- | ------------------------------------- | ------- |
| `ABC`    | ✅        | string                                | -       |
| `CDE`    | ✅        | string:`["A", "B", "C"]` | -       |

### Responses

#### 200 OK

Return type...looks as follows:`{"A": int, "B": int, "C": int}`.

**Example response**:

```json
[
  {
    "A": 0,
    "B": 4,
    "C": 42
  },
  {
    "C": 5,
    "D": 5,
    "E": 54
  },
  {
    "E": 6,
    "F": 19,
    "G": 3
  }
]
```

#### 400 Bad request

Bad Request if parameters are missing or wrong/no type specified

**Example response:**

```json
{
  "error": {
    "code": 400,
    "type": "Bad Request",
    "reasons": "The given reason that triggered the bad request."
  }
}
```

## GET `/`

### Description

Get ...

### Response

#### 200 OK

**Example response**:

```json
[
  {"A": "A", "id": 0}, 
	{"B": "B", "id": 1}, 
]
```
