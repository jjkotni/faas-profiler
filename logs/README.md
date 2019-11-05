The logs folder holds all the out files for a given test. The folders are named by the test name. Each folder consists of the following:
1. SWI.log -> Log file for the invoker
2. WA.log  -> Log file for the workload analyzer
3. perf-mon.out -> Perf stats in case it was part of the monitoring script
4. test_metadata.out -> Metadata for each test, holds when the test was invoked, useful to query CouchDB
