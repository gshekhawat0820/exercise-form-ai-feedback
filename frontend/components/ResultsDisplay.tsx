'use client';

import { CheckCircle, RotateCcw, Calendar, Layers } from 'lucide-react';
import { formatTimestamp } from '@/lib/utils';
import { AnalyzeResponse } from '@/lib/api';

interface ResultsDisplayProps {
  result: AnalyzeResponse;
  onReset: () => void;
}

export default function ResultsDisplay({ result, onReset }: ResultsDisplayProps) {
  // Parse feedback sections
  const parseFeedback = (feedback: string) => {
    const sections: { title: string; content: string }[] = [];
    
    // Try to split by common patterns (numbered lists, bullet points, etc.)
    const lines = feedback.split('\n');
    let currentSection = { title: 'Feedback', content: '' };
    
    lines.forEach((line) => {
      const trimmed = line.trim();
      if (trimmed) {
        // Check if it's a header (all caps or ends with colon)
        if (trimmed.match(/^[A-Z\s]+:$/)) {
          if (currentSection.content) {
            sections.push({ ...currentSection });
          }
          currentSection = { title: trimmed.replace(':', ''), content: '' };
        } else {
          currentSection.content += (currentSection.content ? '\n' : '') + trimmed;
        }
      }
    });
    
    if (currentSection.content) {
      sections.push(currentSection);
    }
    
    return sections.length > 0 ? sections : [{ title: 'Feedback', content: feedback }];
  };

  const feedbackSections = parseFeedback(result.feedback);

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Success Header */}
      <div className="bg-green-50 border border-green-200 rounded-xl p-6 flex items-start gap-4">
        <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
          <CheckCircle className="w-6 h-6 text-green-600" />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-green-900 mb-1">
            Analysis Complete!
          </h3>
          <p className="text-sm text-green-700">
            Your exercise form has been analyzed. Review the feedback below to improve your technique.
          </p>
        </div>
        <button
          onClick={onReset}
          className="flex items-center gap-2 text-green-700 hover:text-green-900 font-medium text-sm bg-green-100 hover:bg-green-200 px-4 py-2 rounded-lg transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
          New Analysis
        </button>
      </div>

      {/* Metadata */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white border border-slate-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-slate-600 mb-2">
            <Layers className="w-5 h-5" />
            <span className="text-sm font-medium">Frames Analyzed</span>
          </div>
          <p className="text-2xl font-bold text-slate-900">{result.frames_analyzed}</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-slate-600 mb-2">
            <Calendar className="w-5 h-5" />
            <span className="text-sm font-medium">Analysis Time</span>
          </div>
          <p className="text-lg font-semibold text-slate-900">
            {formatTimestamp(result.timestamp)}
          </p>
        </div>
      </div>

      {/* Feedback Sections */}
      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <div className="bg-gradient-to-r from-primary-500 to-primary-600 px-6 py-4">
          <h2 className="text-xl font-bold text-white">AI Form Feedback</h2>
        </div>
        
        <div className="p-6 space-y-6">
          {feedbackSections.map((section, index) => (
            <div key={index} className="space-y-3">
              {feedbackSections.length > 1 && (
                <h3 className="text-lg font-semibold text-slate-900 flex items-center gap-2">
                  <span className="w-6 h-6 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-sm font-bold">
                    {index + 1}
                  </span>
                  {section.title}
                </h3>
              )}
              <div className="prose prose-slate max-w-none">
                {section.content.split('\n').map((paragraph, pIndex) => {
                  const trimmed = paragraph.trim();
                  if (!trimmed) return null;
                  
                  // Check if it's a numbered list item
                  const numberedMatch = trimmed.match(/^(\d+[\.)]\s*)(.*)/);
                  if (numberedMatch) {
                    return (
                      <div key={pIndex} className="flex gap-3 mb-3">
                        <span className="font-semibold text-primary-600 flex-shrink-0">
                          {numberedMatch[1]}
                        </span>
                        <p className="text-slate-700 leading-relaxed">{numberedMatch[2]}</p>
                      </div>
                    );
                  }
                  
                  // Check if it's a bullet point
                  if (trimmed.startsWith('•') || trimmed.startsWith('-') || trimmed.startsWith('*')) {
                    return (
                      <div key={pIndex} className="flex gap-3 mb-3">
                        <span className="text-primary-600 flex-shrink-0">•</span>
                        <p className="text-slate-700 leading-relaxed">
                          {trimmed.substring(1).trim()}
                        </p>
                      </div>
                    );
                  }
                  
                  // Regular paragraph
                  return (
                    <p key={pIndex} className="text-slate-700 leading-relaxed mb-3">
                      {trimmed}
                    </p>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4">
        <button
          onClick={onReset}
          className="flex-1 bg-primary-600 hover:bg-primary-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
        >
          Analyze Another Video
        </button>
        <button
          onClick={() => {
            const text = `Exercise Form Feedback\n\nAnalysis Date: ${formatTimestamp(result.timestamp)}\nFrames Analyzed: ${result.frames_analyzed}\n\n${result.feedback}`;
            navigator.clipboard.writeText(text);
            alert('Feedback copied to clipboard!');
          }}
          className="bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold py-3 px-6 rounded-lg transition-colors"
        >
          Copy Feedback
        </button>
      </div>
    </div>
  );
}
