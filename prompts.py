from langchain.prompts import PromptTemplate

def refine_question_prompt():
    return PromptTemplate(
        template="""
        Refine the following question to be more specific and detailed as a legal question, which is detailed and well-organized.

        Original Question: {user_question}

        Refined Question:
        """,
        input_variables=["user_question"]
    )

def extract_key_case_info():
    return PromptTemplate(
        template="""
        Extract the key information from the provided legal case file. Focus on accurately identifying and extracting the following:

        1. Case Name and Number: Ensure the case number is in the correct format, including any dashes, letters, or special characters.
        2. Parties Involved: Who are the plaintiff(s), defendant(s), or other relevant parties?
        3. Court Information: Extract the full court name and jurisdiction.
        4. Date Filed and Relevant Dates: When was the case initially filed? Include other relevant dates, like incident dates, trial dates, etc.
        5. Cause of Action: What are the primary legal claims, issues, or charges (e.g., negligence, breach of contract, etc.)?
        6. Key Facts: What are the most important factual details of the case? Focus on the facts that are central to the legal dispute.
        7. Procedural History: What significant motions, hearings, or decisions have occurred (e.g., rulings, appeals, summary judgment, etc.)?
        8. Current Status: What is the present stage of the case (e.g., ongoing trial, awaiting appeal, etc.)?
        9. Evidence and Witnesses: What evidence has been presented, and who are the key witnesses?
        10. Potential Outcomes: What are the possible outcomes or remedies being sought?
        11. Legal Implications: What are the broader legal implications of the case?

        Provide as much detail as possible for each point, and ensure that the case number, court, and filing date are accurate.

        Context:
        {context}
        """,
        input_variables=["context"]
    )

def followup_case_questions():
    return PromptTemplate(
        template="""
        Based on the initial information extracted, please answer the following follow-up questions:

        1. Are there any precedent cases cited that could significantly impact this case?
        2. What are the main legal arguments presented by each party?
        3. Are there any expert witnesses mentioned, and if so, what is their role?
        4. What potential damages or remedies are being sought?
        5. Are there any notable legal or factual disputes between the parties?
        6. Have there been any settlement discussions or alternative dispute resolution attempts?
        7. Are there any upcoming critical deadlines or hearing dates?
        8. What are the potential precedents or legal implications of this case?
        9. What are the broader legal or industry implications of this case?

        Use the provided context and perform an additional vector search if necessary to answer these questions. Ensure the accuracy of the extracted case number, court, and filing date.

        Initial Context:
        {initial_context}

        Additional Context (if needed):
        {additional_context}
        """,
        input_variables=["initial_context", "additional_context"]
    )

def consolidate_and_summarize_case():
    return PromptTemplate(
        template="""
        Using all the information gathered, create a comprehensive and accurate summary of the legal case. Include the following sections:

        1. Case Overview
           - Case Name and Number: Ensure the case number includes any dashes, letters, or special characters.
           - Parties Involved: Plaintiff(s), Defendant(s), or other parties.
           - Court Information: Ensure the correct court name and jurisdiction are captured.
           - Dates: Capture the relevant dates (filing date, incident date, decision dates, etc.).
        2. Factual Background
           - Key Events Leading to the Case: Provide key details of the events or transactions leading to the case.
           - Relevant Dates and Timelines: List important dates that are crucial to understanding the case.
        3. Legal Issues
           - Primary Causes of Action: Identify the legal claims, issues, or charges in the case (e.g., contract breach, negligence, criminal charges, etc.).
           - Key Legal Arguments (Plaintiff/Defendant): Summarize the legal arguments presented by both sides.
        4. Procedural History
           - Significant Motions Filed: Identify key motions (e.g., summary judgment, dismissal, etc.).
           - Important Rulings: Summarize significant rulings and decisions.
           - Current Status of the Case: Outline the current procedural stage (trial, appeal, etc.).
        5. Evidence and Witnesses
           - Key Evidence Presented: Summarize key pieces of evidence.
           - Expert Witnesses (if any): Include any expert witnesses and their role in the case.
        6. Potential Outcomes
           - Possible Damages or Remedies: Discuss possible outcomes and remedies (e.g., damages, injunction, etc.).
           - Settlement Prospects (if discussed): Summarize any potential or ongoing settlement discussions.
        7. Upcoming Milestones
           - Critical Deadlines: Include any important deadlines or filing requirements.
           - Scheduled Hearings or Trial Dates: List upcoming court dates or hearings.
        8. Analysis and Implications
           - Potential Precedents: Discuss any potential legal precedents the case may set.
           - Broader Legal or Industry Impact: Discuss the case's potential impact on the industry, society, or law.

        Ensure that all critical information from the original case file is included, providing a clear and detailed overview of the case.

        Initial Findings:
        {initial_findings}

        Follow-up Information:
        {followup_info}
        """,
        input_variables=["initial_findings", "followup_info"]
    )

def qa_prompt():
    return PromptTemplate(
        template="""
        You are a legal assistant. Answer the following legal question based on the provided context. 
        If the question is asking for a specific date (like when the case was filed, heard, or decided), provide only the relevant date.
        If the answer is not in the context, respond with "I don't know."

        Question:
        {user_question}

        Context:
        {context}

        Answer:
        """,
        input_variables=["user_question", "context"]
    )



def conversational_qa_prompt():
    return PromptTemplate(
        template="""
        You are a helpful legal assistant. Use the conversation history and the provided context to answer the user's question.

        Chat History:
        {chat_history}

        Question:
        {question}

        Context:
        {context}

        Answer:
        """,
        input_variables=["chat_history", "question", "context"]
    )
