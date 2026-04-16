

2026-04-02: b/498921412 Piggyback features
2026-04-02: b/498921412 Suggest here or in the investigator skill to add `evidence/` folder which builds up local evidence stuff.
2026-04-02: b/498907488 Add/use `gemini-session-sbobinator` to add evidence on investigation. Stuff like: when did Gemini CLI start the investigation? when did we do that fatal `kubectl XXX drain`? This can be seen by looking smart at Gemini CLI logs. That's in ruby so might have to port it to python.
**Note**: every time I call the  `gemini-session-sbobinator` from bash, it works great, but when i call it from within GEMINI CLI it crashes the program, I don't know why. My intuitioin is that its reading a JSON file which is being open and `in fieri`.
