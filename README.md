# kvbench
Benchmarking tool for NoSQL databases K(ey) V(alue) Bench(mark)

1. Store KV
2. Read KV
3. Indexed List of KV's
4. KV Definition (for KV Bench)
5. Pre Benchmark data prime
6. Benchmark Definition
7. Why KV Bench


1) Store KV
	Key and Value pair will be created as per 4. KV Definition , then submitted to server to store

2) Read KV
	Key and Value pair will be requested from the server by the key.

3) List Generation (Index / Query test)
	3.1. Retrieve a list of Key and Value pairs where seconds is between 2 values
	3.2. Retrieve a list of valid values for summary, along with a count of Key and Value pair matches
	3.3. Retrieve a list of Key and Value pairs that match summary

4) KV Definition
	Key: KVB_<ThreadId>_<UUID>
	Value: JSON Value:
		{
			"key": string,
			"seconds": float,
			"summary": string,
			"description": string,
		}

5) Pre Benchmark data prime
	Prior to Benchmarking it is necessary to have some data in the system to be read and
	for working the indexes.
	This Pre Benchmark data prime process will run 100 threads, each thread will create
	2,000 Key Value pairs to be stored. This will give an initial starting data of 200,000
	Key Value pairs.
	This Pre Benchmark data prime process will not be included in the bench mark result.

6) Benchmark Definition
	The benchmark process will run in 3 phases, to simulate 3 differing workloads, The final
	benchmark figure / result will be an average of the 3 phases.
	Each phase will run 50 threads, each thread will run 10 iterations of the steps described
	below for each phase. There will be a randomly selected wait time of between 100ms (0.1s) and
	1000ms (1.0s) between each step.
	Each phase will ramp up at a rate of 1 thread per second untill all 50 threads are started, and
	will wait until all threads have completed before moving to the next phase.

	6.1) Benchmark results
		6.1.1) For each phase the following results will be produced:
			1. Average write time
			2. Average read time
			3. Average time for List generation 3.1
			4. Average time for List generation 3.2
			5. Average time for List generation 3.3
			6. Average time for all time measures in phase (Note: this is not the same as an average of 1-5 above)
		6.1.2) The average of the 6 result types for all phases will also be produced with the average of
			result type 6 for all phases used as the final bench mark score.

	6.2) Phase 1 simulates a write heavy load scenario, this scenario will perform 2 writes for every read.
		12x Write, 6x Read, 3 Search (index query)
		Each iteration in this phase will:
			1. Write 3 new Key Value pair.
			2. Query a list of documents based on seconds is between 2 values (3.1)
			3. Select 2 documents at random from list and retrieve them
			4. Write 3 new Key Value pair.
			5. Query a list of valid values for summary (3.2)
			6. Write 3 new Key Value pair.
			7. Query a list of documents based on summary selected at random from previous list (3.3)
			8. Select 2 documents at random from list and retrieve them
			9. Write 3 new Key Value pair.

	6.3) Phase 2 simulates a indexing / query heavy load scenario, this scenario will perform 2 reads for every write.
		1x Write, 2x Read, 6 Search (index query)
		Each iteration in this phase will:
			1. Write a new Key Value pair.
			2. Query a list of documents based on seconds is between 2 values (3.1) x2
			3. Select a document at random from list and retrieve it
			4. Query a list of valid values for summary (3.2) x3
			5. Query a list of documents based on summary selected at random from previous list (3.3)
			6. Select a document at random from list and retrieve it

	6.4) Phase 3 simulates a read heavy load scenario, this scenario will perform 10 reads for every write.
		1x Write, 10x Read, 3 Search (index query)
		Each iteration in this phase will:
			1. Write a new Key Value pair.
			2. Query a list of documents based on seconds is between 2 values (3.1)
			3. Select 5 documents at random from list and retrieve them
			5. Query a list of valid values for summary (3.2)
			5. Query a list of documents based on summary selected at random from previous list (3.3)
			6. Select 5 documents at random from list and retrieve them


7) Why KV Bench

	The following is diferct from <http://guide.couchdb.org/draft/performance.html>:

	A Call to Arms
We're in the market for databases and key/value stores. Every solution has a sweet spot in terms of data, hardware, setup, and operation, and there are enough permutations that you can pick the one that is closest to your problem. But how to find out? Ideally, you download and install all possible candidates, create a profiling test suite with proper testing data, make extensive tests, and compare the results. This can easily take weeks, and you might not have that much time.

We would like to ask developers of storage systems to compile a set of profiling suites that simulate different usage patterns of their systems (read-heavy and write-heavy loads, fault tolerance, distributed operation, and many more). A fault-tolerance suite should include the steps necessary to get data live again, such as any rebuild or checkup time. We would like users of these systems to help their developers find out how to reliably measure different scenarios.

We are working on CouchDB, and we'd like very much to have such a suite! Even better, developers could agree (a far-fetched idea, to be sure) on a set of benchmarks that objectively measure performance for easy comparison. We know this is a lot of work and the results may still be questionable, but it'll help our users a great deal when figuring out what to use.
