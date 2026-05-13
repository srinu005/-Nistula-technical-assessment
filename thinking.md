# Question A: The Immediate Response

 We really sorry for the hot water problem. Our maintenance team will be at the villa by 8:00 AM to resolve the issue.
 Regarding your refund request, I have send highest priority message to our  manager to immediate review once they are online this morning. 

 # Question B: The System Design

Classification & Logging:
 The MessageOrchestrator tags the message as query_type: complaint and action: escalate. The record is saved in the messages table with a priority_level: high flag.

Instant Notification:
 An asynchronous task is triggered to send an Urgent SMS and WhatsApp alert to the Villa B1 caretaker and the local Property Manager via the  API.


 # Question C: The Learning

 I would build an "Issue Sentinel" service that queries the messages table weekly. If the same property_id triggers the same query_type (complaint) with similar keywords ("hot water") more than twice in 60 days, it auto-generates a Maintenance Debt Ticket.