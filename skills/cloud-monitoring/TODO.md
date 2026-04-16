
## Script python TODOs

### TODO1: add to python script the granularity. Maybe of some sort of autogranuilarity:

--granularity 5m|1h|10s|1d|5h30m|AUTO default=AUTO

If default, the granularity is chose to something which keeps metrics between 50 and 1000. 
Eg, if delta T is 1h, choose anything above 3s say 5s.

### TODO2: add ability to add filters

Eg, where node=`my-node-123` or region=`us-central1`, ... maybe in the form of a generic --filter "key=value,key2=value2" or maybe respect some sort of generic gcloud filtering mechanism "(>=" vs "gt" and so on: lets not create a new parser!)