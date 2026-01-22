 #!/bin/bash
 
 start=$(date +%s)

 "$@" &
 pid=$!

 while kill -0 $pid 2>/dev/null; do
	 now=$(date +%s)
	 elapsed=$((now - start))
	 echo "Running for ${elapsed}s"
	 sleep 1
done

wait $pid
