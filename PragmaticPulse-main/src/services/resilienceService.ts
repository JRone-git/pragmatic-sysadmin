// Rule-based resilience scoring system
// No API calls needed - works 100% offline

type Answer = {
  questionId: string;
  questionText: string;
  answer: string;
  score: number;
};

type ScenarioScoring = {
  [questionId: string]: {
    [answer: string]: number;
  };
};

// Scoring weights for each answer option (higher = more resilient)
const SCENARIO_SCORING: ScenarioScoring = {
  // Lost Phone scenario
  '2fa': {
    'Backup codes printed': 25,
    'Cloud sync (Authy/Google)': 15,
    'I don\'t have a backup': 0,
    'SMS (risky)': 5,
  },
  'find-my': {
    'Yes, and I know the login': 25,
    'Yes, but I need 2FA to log in': 10,
    'No': 0,
    'Unsure': 5,
  },
  'backup': {
    'Within 24 hours': 25,
    'Weekly': 15,
    'Monthly': 5,
    'Never': 0,
  },

  // Email Breach scenario
  'password': {
    'Yes, in a password manager': 30,
    'Unique but memorized': 20,
    'Reused across sites': 5,
    'Simple/Common': 0,
  },
  'recovery': {
    'Yes, and verified': 25,
    'Yes, but old': 10,
    'No recovery set': 0,
    'Unsure': 5,
  },
  '2fa-type': {
    'Hardware Key (YubiKey)': 30,
    'App (TOTP)': 20,
    'SMS': 5,
    'None': 0,
  },

  // Cloud Failure scenario
  'local-copy': {
    'Yes, automated daily': 30,
    'Yes, manual monthly': 15,
    'No, cloud only': 0,
    'I have a second cloud': 20,
  },
  'offline': {
    'Yes, synced locally': 25,
    'Some, but not all': 15,
    'No, requires internet': 0,
    'Unsure': 5,
  },
  'export': {
    'Yes, recently': 25,
    'Once, long ago': 10,
    'No': 0,
    'What is that?': 5,
  },
};

// Critical failure point mappings (lowest score = biggest vulnerability)
const FAILURE_POINTS: { [scenario: string]: { [questionId: string]: string } } = {
  'lost-phone': {
    '2fa': 'You have no backup method to access your accounts when your phone is gone. A single lost device locks you out of everything.',
    'find-my': 'Without Find My enabled, you cannot locate, lock, or remotely wipe your device. You lose both the device AND control over your data.',
    'backup': 'No recent backup means all data on that device is gone forever when it\'s lost. Photos, messages, documents - all vanished.',
  },
  'email-breach': {
    'password': 'Your email password is either weak or reused. This is the #1 way attackers compromise accounts - they already have your credentials.',
    'recovery': 'Your recovery options are outdated or missing. If you get locked out, you may never regain access to your own account.',
    '2fa-type': 'You have no two-factor authentication on your most critical account. Without 2FA, your email password is the only thing protecting everything.',
  },
  'cloud-failure': {
    'local-copy': 'You have NO local backup of your cloud data. If the cloud provider has an outage or data loss, you lose everything.',
    'offline': 'You cannot access critical documents without internet. Any connectivity issue leaves you completely blind.',
    'export': 'You\'ve never exported your data. You\'re trusting a third-party with your entire digital life with no escape plan.',
  },
};

// Actionable steps based on answers (dynamically generated)
const GENERIC_STEPS = {
  'lost-phone': [
    'Print backup codes for all critical accounts (email, banking, 2FA) and store them in a secure location like a fireproof safe.',
    'Enable Find My Device on all devices and ensure at least one trusted device can access it without requiring the lost device for authentication.',
    'Set up automated daily backups to an external drive or secondary cloud service. Automate it so you never have to remember.',
  ],
  'email-breach': [
    'Move your most critical accounts (email, banking, social media) to a password manager and generate unique, strong passwords for each.',
    'Enable hardware 2FA (YubiKey) or at minimum an authenticator app (TOTP) on your email. Never use SMS 2FA for your primary email.',
    'Review and update your account recovery options. Add a backup email and phone number you control, not easily accessible from your primary device.',
  ],
  'cloud-failure': [
    'Implement the 3-2-1 backup rule: 3 copies of data, on 2 different media types, with 1 stored offsite (external drive or different cloud).',
    'Set up offline access to critical documents using offline sync features in Google Drive, OneDrive, or similar services.',
    'Use Google Takeout, iCloud export, or your provider\'s export feature quarterly to create local archives of your important data.',
  ],
};

function getScoreForAnswer(questionId: string, answer: string): number {
  const questionScores = SCENARIO_SCORING[questionId];
  if (!questionScores) return 0;
  
  // Try exact match first
  if (questionScores[answer] !== undefined) {
    return questionScores[answer];
  }
  
  // Fallback: partial match (in case text varies slightly)
  for (const [option, score] of Object.entries(questionScores)) {
    if (answer.toLowerCase().includes(option.toLowerCase()) || 
        option.toLowerCase().includes(answer.toLowerCase())) {
      return score;
    }
  }
  
  return 0;
}

function findFailurePoint(answers: Answer[]): { questionId: string; message: string } | null {
  if (answers.length === 0) return null;
  
  // Find the answer with the lowest score
  let lowestScore = Infinity;
  let failureQuestionId = '';
  
  for (const answer of answers) {
    if (answer.score < lowestScore) {
      lowestScore = answer.score;
      failureQuestionId = answer.questionId;
    }
  }
  
  // Map scenario based on question IDs
  let scenarioKey = '';
  if (['2fa', 'find-my', 'backup'].includes(failureQuestionId)) {
    scenarioKey = 'lost-phone';
  } else if (['password', 'recovery', '2fa-type'].includes(failureQuestionId)) {
    scenarioKey = 'email-breach';
  } else if (['local-copy', 'offline', 'export'].includes(failureQuestionId)) {
    scenarioKey = 'cloud-failure';
  }
  
  const failureMessages = FAILURE_POINTS[scenarioKey];
  const message = failureMessages?.[failureQuestionId] || 
    `Critical vulnerability in ${failureQuestionId} - immediate attention required.`;
  
  return { questionId: failureQuestionId, message };
}

function generateCustomSteps(answers: Answer[], scenarioId: string): string[] {
  const steps = [...GENERIC_STEPS[scenarioId as keyof typeof GENERIC_STEPS] || []];
  
  // Customize steps based on specific weak answers
  const lowScoreAnswers = answers.filter(a => a.score <= 5);
  
  if (lowScoreAnswers.length > 0) {
    // Add a fourth step about the specific weakest area
    const weakAreas = lowScoreAnswers.map(a => a.questionText).join(', ');
    steps.push(`URGENT: Address immediate gaps in: ${weakAreas}. These are your most critical vulnerabilities.`);
  }
  
  return steps.slice(0, 4); // Return max 4 steps
}

function generateAssessment(score: number, scenarioId: string): string {
  if (score >= 80) {
    return `Your ${scenarioId.replace('-', ' ')} setup is solid. You've got good habits and proper safeguards in place. Keep testing your recovery procedures quarterly to ensure they still work when you need them.`;
  } else if (score >= 60) {
    return `You're doing okay with ${scenarioId.replace('-', ' ')}, but there's meaningful room for improvement. Address your weakest link soon - when a disaster hits, it won't wait for you to be ready.`;
  } else if (score >= 40) {
    return `Your ${scenarioId.replace('-', ' ')} resilience is concerning. You have some basics in place, but critical gaps remain. A real incident would expose these vulnerabilities. Time to take action.`;
  } else {
    return `Your ${scenarioId.replace('-', ' ')} setup is high-risk. You have significant vulnerabilities that could lead to permanent data loss or account lockout. This should be addressed immediately, not eventually.`;
  }
}

export interface ResilienceResult {
  score: number;
  assessment: string;
  failurePoint: string;
  steps: string[];
}

export function calculateResilience(
  scenarioId: string,
  answers: Record<string, string>
): ResilienceResult {
  // Map scenario title to scenario ID
  const scenarioMap: { [key: string]: string } = {
    'Total Phone Loss': 'lost-phone',
    'Primary Email Breach': 'email-breach',
    'Cloud Storage Wipe': 'cloud-failure',
  };
  
  const mappedScenarioId = scenarioMap[scenarioId] || scenarioId;
  
  // Get question IDs for this scenario
  const scenarioQuestionIds: { [key: string]: string[] } = {
    'lost-phone': ['2fa', 'find-my', 'backup'],
    'email-breach': ['password', 'recovery', '2fa-type'],
    'cloud-failure': ['local-copy', 'offline', 'export'],
  };
  
  const questionIds = scenarioQuestionIds[mappedScenarioId] || [];
  
  // Calculate scores and build answer list
  let totalScore = 0;
  const maxPossibleScore = questionIds.length * 25; // 25 is max per question
  const answerDetails: Answer[] = [];
  
  for (const questionId of questionIds) {
    const answerText = answers[questionId] || Object.keys(SCENARIO_SCORING[questionId] || {})[0];
    const score = getScoreForAnswer(questionId, answerText);
    totalScore += score;
    answerDetails.push({
      questionId,
      questionText: questionId,
      answer: answerText,
      score,
    });
  }
  
  // Normalize to 0-100
  const normalizedScore = maxPossibleScore > 0 
    ? Math.round((totalScore / maxPossibleScore) * 100) 
    : 0;
  
  const failurePoint = findFailurePoint(answerDetails);
  const steps = generateCustomSteps(answerDetails, mappedScenarioId);
  const assessment = generateAssessment(normalizedScore, mappedScenarioId);
  
  return {
    score: normalizedScore,
    assessment,
    failurePoint: failurePoint?.message || 'Multiple areas need attention.',
    steps,
  };
}