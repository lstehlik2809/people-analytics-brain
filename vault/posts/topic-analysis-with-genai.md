---
title: Creating new candidate topic labels on the fly during topic analysis with GenAI
description: Description of a simple hack to simulate the work of a qualitative researcher classifying comments from respondents using GenAI.
date: '2024-02-05'
tags:
- topic-analysis
- employee-survey
- generative-ai
- ai
original: https://blog-about-people-analytics.netlify.app/posts/2024-02-05-topic-analysis-with-genai/
---

One way to use GenAI for topic analysis of employee or customer feedback is to use zero-shot learning and test each comment against a pre-set list of topics that you think cover all relevant themes of interest. 

However, as you can imagine, real people can always surprise you and come up with themes that you hadn't thought of beforehand.

A simple hack to deal with this is to dynamically update the list of candidate topic labels within a loop where GenAI first tries to use the currently existing topic labels to capture the meaning of the comment being analyzed and create new topic label(s) if the existing ones don't match the meaning of the comment. These new labels are then added to the list to be available for analysis of all subsequent comments. 

In another higher-level loop, this analysis can be performed several times to ensure that we capture all the themes present in the corpus of available comments, and that we consider all the identified topic labels for all comments.

The whole process is thus not dissimilar to what a qualitative researcher does when going through the responses of their respondents and classifying those responses using categories based on previous responses or using new categories until new themes stop appearing.

A bit of a challenge may be how to enforce that GenAI comes up with topic labels at a level of abstraction appropriate for a given use case. Based on my experiments, it seems that by providing some examples and counterexamples in the prompt and/or by providing "seed" topic labels at the "right" level of abstraction, you can nudge GenAI to create new labels at the desired level of abstraction.

Below is a short snippet of Python code implementing this approach to topic analysis that you can use for inspiration. Happy topic modeling and exploration 😉 

```python
from openai import OpenAI
client = OpenAI(api_key=myOpenAiApiKey)

# function for detecting topics in comments
def identify_topics(text, topic_labels, item_text):
    prompt = client.chat.completions.create(
        model="gpt-4-1106-preview",
        temperature=0,
        messages=[
            {"role": "system", "content": f"""
            You are a first-class expert in analyzing feedback provided by employees in employee surveys.
            Here is a list of available topic labels for feedback categorization: {','.join(topic_labels)}"""},
            {"role": "user", "content": f"""              
            First, summarize for yourself the feedback provided by an employee. When doing so, be sure to
            consider the wording of the survey item on which the employee has commented to make sure you have
            understood her feedback correctly. Here is the wording of the survey item: {item_text} 
            Then, based on this summarization, from the list of available topic labels, select those that
            accurately capture all important aspects of the employee feedback. You are forbidden to use topic 
            labels that only indirectly or remotely relate to the meaning of employee feedback. Use the topic 
            label only if you are sure that it accurately captures one of the important aspects of employee
            feedback. Don't make things up and report only what is really in the employee feedback.    
            Important: If the topic labels available in the list don't capture some important aspects of employee
            feedback, you must create and use a new topic label or multiple labels to capture these aspects of
            employee feedback. New topic labels must be short, concise, not too general, and specific enough that
            the management can easily understand what the feedback is about. For example, a more specific topic
            label like "HR Ticketing System Problems" would be much better than a more general topic label like 
            "HR System Inefficiencies". 
            As a response provide only a string of relevant topic labels separated by commas, nothing more. 
            Here is the employee's feedback: {text}
            """}
        ]
    )
    response = prompt.choices[0].message.content
    return response

# seed list of candidate topic labels to be enriched during the analysis
topic_labels = []
# higher-level loop for repeating the analysis on all the comments
for run in range(0,3):
    responses = []
    # loop over individual comments
    for row in range(0, df.shape[0]):
        response = identify_topics(text=df.loc[row, 'feedback_text'], topic_labels=topic_labels, item_text=df.loc[row, 'question_text'])
        responses.append(response)
        # extracting identified topics
        identified_topic_labels = response.split(",")
        # removing leading or trailing white space
        identified_topic_labels = [item.strip() for item in identified_topic_labels]
        # enriching the list of candidate topic labels
        topic_labels = topic_labels + identified_topic_labels
        # deduplication of topic labels
        topic_labels = list(set(topic_labels))

# creating field with identified topics in the df
df['topic_labels'] = responses

# adding fields with flags for identified topics for easier filtering of relevant comments
for topic in topic_labels:
    df[topic] = df['topic_labels'].str.contains(topic)

```

<!-- RELATED:BEGIN -->
## Related notes
- [[employee-feedback-analysis-using-openai|Employee feedback analysis using tools from OpenAI]]
- [[sentiment-analysis-validation|Sentiment analysis of employee survey comments using zero-shot classification]]
- [[ai-powered-data-exploration-assistant|Testing my GenAI skepticism]]
- [[rebuilding-a-survey-with-the-help-of-nlp-tools|Rebuilding an employee survey with the help of NLP tools]]
- [[agentic-ai-for-visual-data-exploration|Agentic AI for visual data exploration]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2024-02-05-topic-analysis-with-genai/) on my blog.
