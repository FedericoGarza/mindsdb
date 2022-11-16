# `#!sql CREATE TABLE` Statement

## Description

The `#!sql CREATE TABLE` statement creates a table and fills it with a subselect query output. It is usually used to materialize prediction results as tables.

## Syntax

You can use the usual `CREATE TABLE` statement:

```sql
CREATE TABLE [integration_name].[table_name]
    (SELECT ...);
```

Or the `CREATE OR REPLACE TABLE` statement:

```sql
CREATE OR REPLACE TABLE [integration_name].[table_name]
    (SELECT ...);
```

Here are the steps followed by the syntax:

- It executes a subselect query to get the output dataset.
- In the case of the `CREATE OR REPLACE TABLE` statement, the `[integration_name].[table_name]` table is dropped before recreating it.
- It (re)creates the `[integration_name].[table_name]` table inside the `#!sql [integration_name]` integration.
- It uses the [`#!sql INSERT INTO`](/sql/api/insert/) statement to insert the output of the `#!sql (SELECT ...)` query into the `[integration_name].[table_name]`.

On execution, we get:

```sql
Query OK, 0 rows affected (x.xxx sec)
```

## Example

We want to save the prediction results into the `#!sql int1.tbl1` table.

Here is the schema structure used throughout this example:

```bash
int1
└── tbl1
mindsdb
└── predictor_name
int2
└── tbl2
```

Where:

| Name             | Description                                                                                 |
| ---------------- | ------------------------------------------------------------------------------------------- |
| `int1`           | Integration where the table that stores prediction results resides.                         |
| `tbl1`           | Table that stores prediction results.                                                       |
| `predictor_name` | Name of the model.                                                                          |
| `int2`           | Integration where the data source table used in the inner `#!sql SELECT` statement resides. |
| `tbl2`           | Data source table used in the inner `#!sql SELECT` statement.                               |

Let's execute the query.

```sql
CREATE OR REPLACE TABLE int1.tbl1 (
    SELECT *
    FROM int2.tbl2 AS ta
    JOIN mindsdb.predictor_name AS tb
    WHERE ta.date > '2015-12-31'
);
```

On execution, we get:

```sql
Query OK, 0 rows affected (x.xxx sec)
```