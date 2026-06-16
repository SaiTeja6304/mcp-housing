import React from 'react';

export function parseMarkdown(text: string): React.ReactNode[] {
  const lines = text.split('\n');
  const elements: React.ReactNode[] = [];
  let inCodeBlock = false;
  let codeBlockLines: string[] = [];
  let codeBlockLang = '';
  let keyCounter = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Check code blocks
    if (line.trim().startsWith('```')) {
      if (inCodeBlock) {
        // End code block
        elements.push(
          <pre key={`code-${keyCounter++}`} className="code-block">
            <code className={codeBlockLang}>{codeBlockLines.join('\n')}</code>
          </pre>
        );
        inCodeBlock = false;
        codeBlockLines = [];
        codeBlockLang = '';
      } else {
        // Start code block
        inCodeBlock = true;
        codeBlockLang = line.trim().slice(3);
      }
      continue;
    }

    if (inCodeBlock) {
      codeBlockLines.push(line);
      continue;
    }

    // Check headers
    if (line.startsWith('# ')) {
      elements.push(<h1 key={`h1-${keyCounter++}`}>{parseInline(line.slice(2))}</h1>);
      continue;
    }
    if (line.startsWith('## ')) {
      elements.push(<h2 key={`h2-${keyCounter++}`}>{parseInline(line.slice(3))}</h2>);
      continue;
    }
    if (line.startsWith('### ')) {
      elements.push(<h3 key={`h3-${keyCounter++}`}>{parseInline(line.slice(4))}</h3>);
      continue;
    }

    // Check bullet points
    if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
      const content = line.trim().substring(2);
      elements.push(
        <ul key={`ul-${keyCounter++}`} className="markdown-list">
          <li>{parseInline(content)}</li>
        </ul>
      );
      continue;
    }

    // Empty line -> paragraph separator or space
    if (line.trim() === '') {
      elements.push(<div key={`spacer-${keyCounter++}`} className="markdown-para-space" />);
      continue;
    }

    // Regular line
    elements.push(<p key={`p-${keyCounter++}`} className="markdown-para">{parseInline(line)}</p>);
  }

  return elements;
}

function parseInline(text: string): React.ReactNode {
  const parts: React.ReactNode[] = [];
  let currentText = text;
  let key = 0;

  while (currentText.length > 0) {
    const boldIndex = currentText.indexOf('**');
    const codeIndex = currentText.indexOf('`');
    const linkIndex = currentText.indexOf('[');

    const indices = [
      { type: 'bold', index: boldIndex },
      { type: 'code', index: codeIndex },
      { type: 'link', index: linkIndex }
    ].filter(x => x.index !== -1).sort((a, b) => a.index - b.index);

    if (indices.length === 0) {
      parts.push(currentText);
      break;
    }

    const first = indices[0];
    if (first.index > 0) {
      parts.push(currentText.substring(0, first.index));
      currentText = currentText.substring(first.index);
    }

    if (first.type === 'bold') {
      const closingIndex = currentText.indexOf('**', 2);
      if (closingIndex !== -1) {
        const content = currentText.substring(2, closingIndex);
        parts.push(<strong key={`bold-${key++}`}>{content}</strong>);
        currentText = currentText.substring(closingIndex + 2);
      } else {
        parts.push('**');
        currentText = currentText.substring(2);
      }
    } else if (first.type === 'code') {
      const closingIndex = currentText.indexOf('`', 1);
      if (closingIndex !== -1) {
        const content = currentText.substring(1, closingIndex);
        parts.push(<code key={`inline-code-${key++}`} className="inline-code">{content}</code>);
        currentText = currentText.substring(closingIndex + 1);
      } else {
        parts.push('`');
        currentText = currentText.substring(1);
      }
    } else if (first.type === 'link') {
      const closingBracket = currentText.indexOf(']');
      const openingParen = currentText.indexOf('(', closingBracket);
      const closingParen = currentText.indexOf(')', openingParen);

      if (closingBracket !== -1 && openingParen === closingBracket + 1 && closingParen !== -1) {
        const linkText = currentText.substring(1, closingBracket);
        const linkUrl = currentText.substring(openingParen + 1, closingParen);
        parts.push(
          <a
            key={`link-${key++}`}
            href={linkUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="markdown-link"
          >
            {linkText}
          </a>
        );
        currentText = currentText.substring(closingParen + 1);
      } else {
        parts.push('[');
        currentText = currentText.substring(1);
      }
    }
  }

  return <>{parts}</>;
}
