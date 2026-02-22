# xLLM
<img src="https://github.com/VincentGranville/xLLM/blob/main/xllm_logo4.png">
No Blackbox, secure, accurate, auditable Enterprise AI, developed by BondingAI. Includes AI agents. The links in the PDF documents shared in this folder are clickable only in the eBook version that contains all my papers. The book, entitled <b>No-Blackbox, Secure, Efficient AI and xLLM Solutions</b>, is available <a href="https://mltechniques.com/product/no-blackbox-secure-efficient-ai-and-llm-solutions/">here</a>. For the table of contents, see <a href="https://mltblog.com/4aedKl2">here</a>.

Earlier modules and component can be foundin the older xLLM repository, <a href="https://github.com/VincentGranville/Large-Language-Models">here</a>. I will add the most recent versions in this folder. It includes:

<h2>Base xLLM</h2>

<ol>
<li> <b>Font intelligence</b>: PDF parsing, PDF to JSON, and detection of contextual elements based on font type, relative size and color.
  <li><b>Sorted <i>n</i>-grams</b> that take into account the order of the multitokens in a sentence (the attention mechanism).</li>
  <li><b>Multitoken types</b>: standard, synonyms or found in contextual elements (title, category name, tag, and so on).</li>
  <li><b>Nested hashes</b> as very fast, in-memory native Python database, a better alternative to vector and graph databases.</li>
  <li><b>Multitoken distillation</b> to eliminate redundancy in chunks displayed in the structured answer.</li>
  <li><b>Relevancy scores</b> that tell how relevant a piece of the response is relevant to the prompt.</li>
  <li><b>Trustworthiness scores</b> that tell how reliable the source is, for a specific item in the response.</li>
  <li><b>PMI metric</b> to generate suggested prompts related to the initial query, to reduce prompt engineering</li>
  <li><b>Hierarchical chunking</b> and <b>multi-index</b>.</li>
  <li><b>Multimodal processing</b> to retrieve images, videos, tables and so on, for instance as input for the predictive analytics or data synthesis agents.</li>
  <li><b>xLLM file format</b>: data gathered from corpuses, the Internet, corporate datalabes and repositories are blended and turned into our standardized JSON-like xLLM format before being fed to the response generation engine.</li>
  <li><b>Exact search</b>, broad search, negative keyword search, search by recency, search by category and so on (available from the UI).</li>
  <li><b>Advanced UI</b> allowing fine-tuning in real time with intuitive parameters (explainable AI), access to agents, various types of search, structured output or chat-like response, suggested prompts relevant to your query, relevancy scores and so on. A lot more than a prompt box!</li>
  <li><b>Fine-tuning</b> in real time with intuitive hyperparameter sets, each component having its own set.</li>
  <li><b>Proprietary stemmer / unstemmer</b> and related components (auto-correct, corpus-specific stopwords, building corpus-specific tables of acronyms and synonyms, used as augmentation mechanism)</li>
  <li><b>Evaluation metrics</b>, in particular to assess exhaustivity in the concise response while taking into account the relevancy scores.</li>
  <li><b>Auto-tagging</b>, auto-indexing, taxonomy augmentation to enhance the contextual framework.</li>
  <li><b>Variable length embeddings</b> with alternatives to cosine simularity and dot product to measure correlation between keywords, multitokens, or documents, well suited for sparse correlation tables.</li>
</ol>

<h2>xLLM Deep Neural Network and Related Architecture</h2>

This new material is not in the old repository. It features our proprietary DNN based on explainable AI, as well as an alternative with 100% exact predictions on the training set and 96% correct prediction on the validation set, for next token. It has its own <b>universal functions</b> with explainable parameters, sub-layers but no activation functions, and benefits from <b>benign overfitting</b>, a nice feature present in most DNNs. We use multitokens: for instance 'machine learning conference' is stored as a single multitoken as well as up to 7 sub-multitokens (combinations not in the corpus are ignored), instead of 10 tokens in standard systems. The number of multitokens is 10,000 times smaller than in generic models or specialized models with a generic core.  

<ol>
<li>xLLM's original <b>Deep Neural Network</b></li>
<li>xLLM's alternative based on <b>exact interpolation in 10,000 dimensions</b>, and 96% correct predictions for next token, outside the training set. Used as alternative to PMI metrics and to suggest related keywords in the answer.</li>  
  <li><b>DNN Watermarking</b> to protect your model or data against unauthorized use, with invisible, noise- and distilliation-resistant watermarks</li>
  <li><b>Smart distillation</b> of the DNN parameters (the weights between connected neurons) and/or the input data (tokens), preserving accuracy. Applicable to any DNN, including our own, as well as our DNN alternative.</li>
  <li><b>Anomality Detection Agent</b> with applications in cybersecurity, used in fraud litigation.</li>
  <li><b>NoGAN Data Synthesis</b>, best and fastest on the market, with best evaluation metric.</li>
  <li><b>ECG Agent</b> with better compression rates, to find patterns in ECG (electrocardiogram) data.</li>
</ol>
