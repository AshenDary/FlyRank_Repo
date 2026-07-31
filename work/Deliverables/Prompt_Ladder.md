# The Prompt Ladder — Backend Endpoint Generation

## Baseline (Version 0): The Weak Prompt

**Prompt:**
```
Write backend code.
```

**AI Output:**
```javascript
const express = require('express');
const app = express();
app.use(express.json());

app.get('/api/users', (req, res) => {
  res.json([{ id: 1, name: 'John Doe' }]);
});

app.listen(3000, () => console.log('Server running on port 3000'));
```

**Notes:**
- **What changed in prompt:** Baseline (no changes).
- **What actually improved in output:** Nothing. It generated a generic, bare-minimum Express.js dummy server.
- **What still failed:** It defaulted to JavaScript instead of TypeScript, used Express instead of Fastify/Prisma, hardcoded static fake data, lacked error handling, and ignored modern architectural patterns.
- **What I would try next:** Add a clear goal specifying the exact tech stack and endpoint functionality.

---

## Version 1: Adding a Clear Goal

**Prompt:**
```
Write a Fastify backend POST endpoint in TypeScript that registers a new user using Prisma ORM.
```

**AI Output:**
```typescript
import { FastifyInstance } from 'fastify';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export async function userRoutes(fastify: FastifyInstance) {
  fastify.post('/users', async (request, reply) => {
    const { email, password, name } = request.body as any;
    const user = await prisma.user.create({
      data: { email, password, name },
    });
    return reply.status(201).send(user);
  });
}
```

**Notes:**
- **What changed in prompt:** Added Layer: Clear Goal (specified Fastify, TypeScript, Prisma, and a user registration POST route).
- **What actually improved in output:** The code shifted from a generic Express dummy server to a typed Fastify route using Prisma ORM to create an actual database record.
- **What still failed:** It stores passwords in plain text, uses unsafe `as any` type casting, lacks request validation, and has no try/catch error handling for duplicate email errors.
- **What I would try next:** Add constraints to enforce security and type safety.

---

## Version 2: Adding Constraints

**Prompt:**
```
Write a Fastify backend POST endpoint in TypeScript that registers a new user using Prisma ORM.

Constraints:
- Never store plain text passwords; hash passwords using bcrypt.
- Do not use any types.
- Do not return the password hash in the JSON response.
```

**AI Output:**
```typescript
import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcrypt';

const prisma = new PrismaClient();

interface RegisterUserBody {
  email: string;
  password: string;
  name?: string;
}

export async function userRoutes(fastify: FastifyInstance) {
  fastify.post('/users', async (request: FastifyRequest<{ Body: RegisterUserBody }>, reply: FastifyReply) => {
    const { email, password, name } = request.body;
    const hashedPassword = await bcrypt.hash(password, 10);

    const user = await prisma.user.create({
      data: { email, password: hashedPassword, name },
      select: { id: true, email: true, name: true, createdAt: true }
    });

    return reply.status(201).send(user);
  });
}
```

**Notes:**
- **What changed in prompt:** Added Layer: Constraints (prohibited plain text passwords, `any` types, and leaking password hashes in responses).
- **What actually improved in output:** The output automatically introduced bcrypt password hashing, introduced strong TypeScript request body interfaces, and selectively excluded sensitive user credentials from the JSON response.
- **What still failed:** If a user submits an invalid email or a duplicate email, the server crashes with an unhandled Prisma 500 database error.
- **What I would try next:** Add real context regarding project structure and database schemas.

---

## Version 3: Adding Real Context

**Prompt:**
```
Write a Fastify backend POST endpoint in TypeScript that registers a new user using Prisma ORM.

Constraints:
- Never store plain text passwords; hash passwords using bcrypt.
- Do not use any types.
- Do not return the password hash in the JSON response.

Context:
Our project uses Fastify v4 plugin architecture. Prisma client is decorated on the
Fastify instance (fastify.prisma). The database schema includes a unique constraint
on User.email.
```

**AI Output:**
```typescript
import { FastifyPluginAsync } from 'fastify';
import bcrypt from 'bcrypt';

interface RegisterBody {
  email: string;
  password: string;
  name?: string;
}

const userRoutes: FastifyPluginAsync = async (fastify) => {
  fastify.post<{ Body: RegisterBody }>('/users', async (request, reply) => {
    const { email, password, name } = request.body;

    const existingUser = await fastify.prisma.user.findUnique({ where: { email } });
    if (existingUser) {
      return reply.status(400).send({ error: 'Email already registered' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    const newUser = await fastify.prisma.user.create({
      data: { email, password: hashedPassword, name },
      select: { id: true, email: true, name: true, createdAt: true },
    });

    return reply.status(201).send(newUser);
  });
};

export default userRoutes;
```

**Notes:**
- **What changed in prompt:** Added Layer: Real Context (explained Fastify v4 plugin patterns, `fastify.prisma` instance decoration, and unique email constraints).
- **What actually improved in output:** It removed standalone `new PrismaClient()` instantiation and correctly accessed `fastify.prisma`. It also added an explicit database check for duplicate emails.
- **What still failed (Honest Moment):** This actually introduced a subtle regression. The manual `findUnique` email check introduced a race condition under high concurrency instead of catching Prisma's native `P2002` unique constraint error inside a try/catch block. Additionally, it still lacks runtime payload validation (e.g., accepting empty password strings).
- **What I would try next:** Add a specified output format using Fastify's native JSON Schema validation.

---

## Version 4: Adding Specified Output Format

**Prompt:**
```
Write a Fastify backend POST endpoint in TypeScript that registers a new user using Prisma ORM.

Constraints:
- Never store plain text passwords; hash passwords using bcrypt.
- Do not use any types.
- Do not return the password hash in the JSON response.

Context:
Our project uses Fastify v4 plugin architecture. Prisma client is decorated on the
Fastify instance (fastify.prisma). The database schema includes a unique constraint
on User.email.

Output Format:
Use Fastify route schema validation (JSON Schema) for the request body to validate
that email is a valid email string and password is at least 8 characters long.
```

**AI Output:**
```typescript
import { FastifyPluginAsync } from 'fastify';
import bcrypt from 'bcrypt';

const userRoutes: FastifyPluginAsync = async (fastify) => {
  fastify.post('/users', {
    schema: {
      body: {
        type: 'object',
        required: ['email', 'password'],
        properties: {
          email: { type: 'string', format: 'email' },
          password: { type: 'string', minLength: 8 },
          name: { type: 'string' }
        }
      },
      response: {
        201: {
          type: 'object',
          properties: {
            id: { type: 'string' },
            email: { type: 'string' },
            name: { type: 'string' },
            createdAt: { type: 'string' }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { email, password, name } = request.body as { email: string; password: string; name?: string };

    try {
      const hashedPassword = await bcrypt.hash(password, 10);
      const newUser = await fastify.prisma.user.create({
        data: { email, password: hashedPassword, name },
        select: { id: true, email: true, name: true, createdAt: true },
      });
      return reply.status(201).send(newUser);
    } catch (error: any) {
      if (error.code === 'P2002') {
        return reply.status(409).send({ message: 'Email already exists' });
      }
      throw error;
    }
  });
};

export default userRoutes;
```

**Notes:**
- **What changed in prompt:** Added Layer: Specified Output Format (mandated Fastify JSON Schema validation for request payload and response serialization).
- **What actually improved in output:** The route now automatically rejects malformed requests (like short passwords or bad emails) before code execution starts. It also fixed the race condition from V3 by properly catching Prisma's `P2002` error code.
- **What still failed:** Error responses are unstructured, and there are no unit testing guidelines or inline logging setup for operational debugging.
- **What I would try next:** Add quality criteria for production readiness (logging & clean error returns).

---

## Version 5: Adding Quality Criteria

**Prompt:**
```
Write a Fastify backend POST endpoint in TypeScript that registers a new user using Prisma ORM.

Constraints:
- Never store plain text passwords; hash passwords using bcrypt.
- Do not use any types.
- Do not return the password hash in the JSON response.

Context:
Our project uses Fastify v4 plugin architecture. Prisma client is decorated on the
Fastify instance (fastify.prisma). The database schema includes a unique constraint
on User.email.

Output Format:
Use Fastify route schema validation (JSON Schema) for the request body to validate
that email is a valid email string and password is at least 8 characters long.

Quality Criteria:
The code must be production-ready: include structured log statements using
request.log, return clean RFC-compliant error payloads ({ statusCode, error,
message }), and export the route in a self-contained module suitable for
enterprise repositories.
```

**AI Output:**
```typescript
import { FastifyPluginAsync } from 'fastify';
import { Prisma } from '@prisma/client';
import bcrypt from 'bcrypt';

interface RegisterRequestBody {
  email: string;
  password: string;
  name?: string;
}

export const userRoutes: FastifyPluginAsync = async (fastify): Promise<void> => {
  fastify.post<{ Body: RegisterRequestBody }>(
    '/users',
    {
      schema: {
        summary: 'Register a new user',
        tags: ['Users'],
        body: {
          type: 'object',
          required: ['email', 'password'],
          properties: {
            email: { type: 'string', format: 'email' },
            password: { type: 'string', minLength: 8 },
            name: { type: 'string', minLength: 1 },
          },
        },
        response: {
          201: {
            type: 'object',
            properties: {
              id: { type: 'string' },
              email: { type: 'string' },
              name: { type: 'string', nullable: true },
              createdAt: { type: 'string' },
            },
          },
        },
      },
    },
    async (request, reply) => {
      const { email, password, name } = request.body;

      request.log.info({ email }, 'Attempting user registration');

      try {
        const hashedPassword = await bcrypt.hash(password, 10);

        const newUser = await fastify.prisma.user.create({
          data: {
            email,
            password: hashedPassword,
            name,
          },
          select: {
            id: true,
            email: true,
            name: true,
            createdAt: true,
          },
        });

        request.log.info({ userId: newUser.id }, 'User registered successfully');

        return reply.status(201).send(newUser);
      } catch (error) {
        if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === 'P2002') {
          request.log.warn({ email }, 'Registration failed: Email collision');
          return reply.status(409).send({
            statusCode: 409,
            error: 'Conflict',
            message: 'A user with this email address already exists.',
          });
        }

        request.log.error({ error }, 'Unexpected error during user registration');
        return reply.status(500).send({
          statusCode: 500,
          error: 'Internal Server Error',
          message: 'An unexpected error occurred. Please try again later.',
        });
      }
    }
  );
};

export default userRoutes;
```

**Notes:**
- **What changed in prompt:** Added Layer: Quality Criteria (demanded production-ready logging, structured error objects, and clean modular exports).
- **What actually improved in output:** The output moved from a raw function to an enterprise-grade backend endpoint. It features structured Fastify pino logging at each lifecycle stage, safe Prisma error handling without leaking stack traces, and strict schema validation.
- **What still failed:** Nothing within the scope of this single endpoint.
- **What I would try next:** This prompt has reached production readiness for single-route generation.

---

## Final Reusable Prompt

Cleaned up so anyone on the track can copy and run it without needing context from me:

```
Act as a Senior Backend Engineer. Write a production-ready Fastify POST endpoint in TypeScript for user registration using Prisma ORM.

### Tech Stack & Architecture:
- Framework: Fastify (v4) with plugin architecture (FastifyPluginAsync).
- ORM: Prisma Client decorated on the Fastify instance (fastify.prisma).
- Language: TypeScript with strict typing (no `any` or `as any` casting).

### Route Requirements:
- Path: /users
- Action: Register a new user with hashed passwords using bcrypt.
- Fields: email, password (min 8 characters), and optional name.

### Route Constraints & Validation:
1. Use Fastify route JSON Schema validation for request payload (email format, password minLength: 8) and 201 response serialization.
2. Never store or leak plain text passwords or password hashes in the response payload.
3. Catch Prisma's native P2002 duplicate key error and return a structured HTTP 409 Conflict payload.
4. Include structured Fastify logging (request.log.info, request.log.warn, request.log.error).
5. Format all error responses as standard JSON objects: { statusCode, error, message }.
```
