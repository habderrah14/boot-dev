# Glossary

A cross-module glossary of terms used in the book. Entries are grouped by the module where the term first appears, but they show up repeatedly across the curriculum.

## A

- **Abstraction.** Hiding implementation details behind a simpler interface. See Module 04 ch. 04.
- **Algorithm.** A finite sequence of unambiguous steps that solves a class of problems. See Module 06 ch. 01.
- **API (Application Programming Interface).** The contract a library, service, or module exposes to its users.
- **Argument.** A value passed to a function when it is called. Contrast *parameter*.
- **Arity.** The number of arguments a function accepts.
- **Array.** A contiguous sequence of elements indexed by integers. In Python, closest analogue is `list`; in TypeScript, `Array<T>`.
- **Authentication (AuthN).** Proving *who* a request is from. See Module 12 ch. 07.
- **Authorization (AuthZ).** Deciding *what* an authenticated principal may do. See Module 12 ch. 08.

## B

- **Backpressure.** A mechanism that signals upstream producers to slow down when consumers cannot keep up (bounded queues, flow control, `429` responses). See [appendix-system-design](appendix-system-design.md) and Module 15.
- **Big-O.** Asymptotic upper bound on a function's growth rate. See Module 06 ch. 03.
- **Branch.** A movable pointer to a commit in Git. See Module 03 ch. 05.

## C

- **CAP theorem.** In the presence of a network **partition**, a distributed store must trade off **consistency** vs **availability**; latency ties to the same real-world constraints. See [appendix-system-design](appendix-system-design.md).
- **Callback.** A function passed to another function to be called later.
- **CDN (Content Delivery Network).** Geographically-distributed edge caches serving static assets. See Module 13 ch. 07.
- **Closure.** A function together with the lexical environment it captured. See Module 05 ch. 06.
- **Commit.** An immutable snapshot in Git. See Module 03 ch. 02.
- **Container.** An isolated process with its own filesystem and namespaces. See Module 14 ch. 02.
- **CRUD.** Create, Read, Update, Delete — the four basic operations on stored data.
- **Currying.** Transforming `f(a, b, c)` into `f(a)(b)(c)`. See Module 05 ch. 07.

## D

- **Decorator.** A higher-order function that wraps another function, returning a new function with added behavior. See Module 05 ch. 08.
- **DNS.** Domain Name System — maps hostnames to IP addresses. See Module 10 ch. 02.
- **Docker.** Tooling and runtime for building and running containers. See Module 14.

## E

- **Encapsulation.** Bundling data with the methods that operate on it, and limiting outside access. See Module 04 ch. 03.
- **Event loop.** The single-threaded scheduler that drives JavaScript runtimes. See Module 08 ch. 13.
- **Eventual consistency.** A consistency model where replicas may temporarily disagree but converge over time (DNS, caches, async DB replicas). See [appendix-system-design](appendix-system-design.md).

## F

- **First-class function.** A function that can be passed, returned, and stored like any other value. See Module 05 ch. 02.
- **Function.** A named, reusable block of logic that may take inputs and return an output.

## G

- **Generic.** A type or function parameterized over types. See Module 09 ch. 13.
- **Graph.** A set of nodes (vertices) connected by edges. See Module 06 ch. 14.

## H

- **Hashmap / Dictionary / Object.** Data structure mapping keys to values with average O(1) lookup. See Module 06 ch. 12.
- **Heap.** (1) A region of memory for dynamically-allocated objects. (2) A tree-based priority queue. Context disambiguates.
- **HTTP.** HyperText Transfer Protocol — the application-layer protocol of the web. See Modules 10 and 12.

## I

- **Idempotency key.** A client-supplied stable identifier (often a UUID) so duplicate retries of the same logical operation do not create duplicate side effects (payments, orders). See [appendix-system-design](appendix-system-design.md) and Module 12 ch. 09 (webhooks).
- **Idempotent.** An operation that produces the same result when applied multiple times.
- **Inheritance.** A class (child) acquiring attributes and methods from another class (parent). See Module 04 ch. 05.
- **Interface.** A named shape that a value can conform to. See Module 09 ch. 08.

## J

- **JSON.** JavaScript Object Notation — a text-based data interchange format. See Module 10 ch. 06.
- **Junior backend spine (appendix).** Curated post-path topics: structured logging, testing layers, migrations, 12-factor config, REST ergonomics. See [appendix-junior-backend.md](appendix-junior-backend.md).
- **JWT vs session cookie.** **JWTs** are self-contained signed tokens (stateless verification, revocation is harder). **Server-side sessions** store opaque IDs in cookies and keep state in a datastore (easier revocation, requires sticky sessions or shared store). See Module 12 ch. 07.

## L

- **Linked list.** Data structure where each node points to the next (and possibly previous). See Module 06 ch. 09.
- **Load balancer.** A server that distributes requests across a pool of backends.

## M

- **Merge.** Combining two Git branches into one. See Module 03 ch. 06.
- **Middleware.** A function that runs between receiving a request and sending a response.
- **Mutation.** Changing the value of an existing piece of state in place.

## N

- **Namespace.** A container for names that prevents collisions.
- **Normalization.** Structuring a relational database to minimize redundancy. See Module 11 ch. 09.

## O

- **OCI image.** Open Container Initiative image format — immutable layers + manifest consumed by Docker/containerd. See Module 14 ch. 06.
- **Object storage.** Storage model for arbitrary blobs, keyed by a string, with no filesystem semantics. See Module 13 ch. 04.
- **OOP.** Object-oriented programming. See Module 04.
- **OWASP Top 10.** Curated list of common web risks (injection, broken access control, SSRF, etc.) used as a checklist, not a guarantee of coverage. See [appendix-system-design](appendix-system-design.md) and Module 12.

## P

- **p99 latency.** The 99th percentile response time — tail latency that drives timeouts and SLOs; contrast with p50 (median). See [appendix-system-design](appendix-system-design.md) and Module 10 ch. 04.
- **Parameter.** A name in a function's signature; a placeholder for an argument.
- **Polymorphism.** Many shapes. Code that works uniformly over different concrete types. See Module 04 ch. 06.
- **Promise.** An object representing a future value in JavaScript. See Module 08 ch. 12.
- **Pub/Sub.** A messaging pattern where publishers emit events that subscribers consume, decoupled via a broker. See Module 15.
- **Pure function.** A deterministic function with no side effects. See Module 05 ch. 03.

## Q

- **Queue.** FIFO data structure. See Module 06 ch. 08.

## R

- **Rebase.** Moving or replaying Git commits onto a new base. See Module 03 ch. 07.
- **Recursion.** A function calling itself. See Module 05 ch. 04.
- **Retries with jitter.** Exponential backoff plus randomness so many clients do not retry in lockstep after an outage (thundering herd). See [appendix-system-design](appendix-system-design.md) and Module 15 ch. 05.
- **Red-black tree.** A self-balancing binary search tree. See Module 06 ch. 11.
- **Refcounting.** Garbage collection technique tracking the number of references to an object. See Module 07 ch. 10.
- **REST.** Representational State Transfer — an architectural style for HTTP APIs.

## S

- **S3 multipart upload.** API for uploading large objects in parts with resumable progress and checksums per part; critical for big binaries and flaky networks. See Module 13 ch. 03.
- **Set.** An unordered collection of unique elements. See Module 01 ch. 11 and Module 06.
- **Shell.** A command-line interpreter. See Module 02 ch. 01.
- **SQL.** Structured Query Language — the lingua franca of relational databases. See Module 11.
- **Stack.** (1) LIFO data structure. (2) Region of memory for function call frames. See Module 06 ch. 07 and Module 07 ch. 06.
- **Subquery.** A query nested inside another. See Module 11 ch. 08.
- **Sum type / tagged union.** A type that is one of several alternatives. See Module 05 ch. 09.

## T

- **TCP.** Transmission Control Protocol — the reliable, ordered transport underlying HTTP.
- **Trie.** A tree for storing strings where each edge represents a character. See Module 06 ch. 13.
- **TypeScript.** Typed superset of JavaScript. See Module 09.

## U

- **Union type.** A type that is one of several alternatives, discriminated at runtime. See Module 09 ch. 03.
- **URI / URL.** Uniform Resource Identifier / Locator. See Module 10 ch. 03.

## V

- **Variable.** A named binding to a value.
- **Volume.** Persistent storage attached to a Docker container. See Module 14 ch. 03.

## W

- **Webhook.** A user-configurable HTTP callback. See Module 12 ch. 09.
