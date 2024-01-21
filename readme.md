# TenderML
<h1>Project Details</h1>

<h2>Project Overview</h2>
<p>The primary objective of this project was to develop an AI-based system capable of classifying text and extracting specific information in real-time from PDF files. The focus was on handling a diverse set of PDF documents, specifically contract tender filing information related to construction work. The documents were in German language, and the project involved training an AI model to classify and extract relevant data.</p>

<h2>Project Scope</h2>
<ul>
    <li><strong>Text Classification:</strong> Utilized Support Vector Machines (SVM) to classify text within PDF documents. The training dataset comprised more than 1000 documents with varying formats but consistent contextual content.</li>
    <li><strong>Data Extraction Process:</strong>
        <ul>
            <li>Employed a tree data structure post-classification to obtain generic data.</li>
            <li>Implemented a filtering mechanism to refine and correct the extracted data.</li>
            <li>Utilized Depth-First Search (DFS) to traverse the tree and identify specific information.</li>
        </ul>
    </li>
    <li><strong>Language and Context:</strong>
        <ul>
            <li>The project specifically targeted PDFs containing information related to contract tender filing for construction work.</li>
            <li>All documents were in the German language, requiring language-specific processing.</li>
        </ul>
    </li>
    <li><strong>Deployment:</strong>
        <ul>
            <li>Deployed the solution using FASTAPI on a Ray cluster hosted on an AWS EC2 Instance.</li>
            <li>Leveraged AWS EC2's autoscaling capabilities to ensure efficient resource allocation.</li>
        </ul>
    </li>
    <li><strong>Supervised Learning Approach:</strong> Incorporated a semi-supervised learning approach during SVM training to enhance model performance.</li>
</ul>

<h2>Technologies Used</h2>
<ul>
    <li><strong>Text Classification:</strong> Support Vector Machines (SVM)</li>
    <li><strong>Data Structure:</strong> Tree data structure for hierarchical organization</li>
    <li><strong>Data Extraction:</strong> Depth-First Search (DFS) and Regular Expressions (regex)</li>
    <li><strong>Deployment:</strong> FASTAPI, Ray cluster on AWS EC2 Instance</li>
    <li><strong>Language:</strong> Python</li>
</ul>

<h2>Project Outcome</h2>
<p>The project successfully achieved the goal of classifying and extracting information from diverse PDF documents in real-time with 95% accuracy. The solution's deployment on AWS EC2 with autoscaling ensures scalability, making it suitable for handling varying workloads.</p>

<h2>
    Technical Support
</h2>
<p>
    You can open a support ticket by sending an email here: <a href="mailto:info@recursivedata.com" title="Open Support Ticket">
        info@recursivedata.com
    </a>
</p>

