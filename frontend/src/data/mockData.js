export const projects = [
  {
    id: 'repo-analytics', name: 'RepoAnalytics', emoji: 'RA', color: 'purple',
    description: 'An open-source dashboard for understanding repository health, contributor patterns, and release momentum.',
    longDescription: 'RepoAnalytics turns noisy repository activity into clear signals for maintainers. The team is building a thoughtful set of analytics views that help open-source teams understand where to focus next.',
    stack: ['React', 'Node.js', 'PostgreSQL'], difficulty: 'Intermediate', status: 'In progress', type: 'Open source', contributors: 6, teamSize: 8, owner: 'Maya Chen', ownerUsername: 'mayac', updated: '2 days ago', roles: ['Frontend Developer', 'Data Engineer'], popular: 94,
  },
  {
    id: 'openstudy', name: 'OpenStudy', emoji: 'OS', color: 'blue',
    description: 'A peer-powered study space for sharing notes, finding accountability partners, and learning in public.',
    longDescription: 'OpenStudy is a calm, collaborative learning space for students and self-taught developers. We are making it easy to form small study circles and keep momentum through shared goals.',
    stack: ['Next.js', 'TypeScript', 'Supabase'], difficulty: 'Beginner', status: 'Recruiting', type: 'Community', contributors: 4, teamSize: 6, owner: 'Arjun Rao', ownerUsername: 'arjunrao', updated: '5 hours ago', roles: ['Product Designer', 'Frontend Developer'], popular: 86,
  },
  {
    id: 'devboard', name: 'DevBoard', emoji: 'DB', color: 'orange',
    description: 'A focused personal command center for developers who want their tasks, notes, and ideas in one place.',
    longDescription: 'DevBoard brings together the small things that keep a developer in flow: quick notes, lightweight planning, and a useful view of what is next. The product is deliberately opinionated and fast.',
    stack: ['React', 'Go', 'SQLite'], difficulty: 'Intermediate', status: 'In progress', type: 'Side project', contributors: 3, teamSize: 5, owner: 'Jon Bell', ownerUsername: 'jonbell', updated: '1 day ago', roles: ['UX Researcher'], popular: 78,
  },
  {
    id: 'taskflow', name: 'TaskFlow', emoji: 'TF', color: 'teal',
    description: 'Simple, opinionated project planning for small teams that want to spend more time shipping.',
    longDescription: 'TaskFlow is a tiny project management tool with a strong bias toward clarity. We are exploring how much software small teams really need to stay aligned.',
    stack: ['Vue', 'Python', 'Django'], difficulty: 'Advanced', status: 'Recruiting', type: 'Open source', contributors: 8, teamSize: 10, owner: 'Priya Nair', ownerUsername: 'priyanair', updated: '3 days ago', roles: ['Backend Developer', 'DevOps Engineer'], popular: 91,
  },
  {
    id: 'codeconnect', name: 'CodeConnect', emoji: 'CC', color: 'pink',
    description: 'Find compatible collaborators through shared interests, availability, and the way you like to work.',
    longDescription: 'CodeConnect helps developers move from “we should build something” to a first pull request. We are prototyping matching signals that put working styles alongside technical skills.',
    stack: ['React', 'Python', 'Redis'], difficulty: 'Advanced', status: 'Planning', type: 'Community', contributors: 5, teamSize: 7, owner: 'Nora Wilson', ownerUsername: 'noraw', updated: '1 week ago', roles: ['Machine Learning Engineer'], popular: 83,
  },
  {
    id: 'ai-resume-builder', name: 'AI Resume Builder', emoji: 'AI', color: 'indigo',
    description: 'A transparent, structured resume builder that helps developers tell a more useful career story.',
    longDescription: 'This project is about making resume writing less opaque. We are designing helpful prompts and exportable templates while keeping the developer in control of their story and data.',
    stack: ['React', 'FastAPI', 'OpenAI'], difficulty: 'Intermediate', status: 'Recruiting', type: 'Side project', contributors: 2, teamSize: 5, owner: 'Samir Patel', ownerUsername: 'samirp', updated: '4 days ago', roles: ['Frontend Developer', 'Content Designer'], popular: 88,
  },
  {
    id: 'campushub', name: 'CampusHub', emoji: 'CH', color: 'green',
    description: 'A digital commons for campus clubs to publish events, share resources, and welcome new members.',
    longDescription: 'CampusHub gives student communities a better home than a scattered set of group chats. The first milestone is a fast event and resource discovery experience.',
    stack: ['Svelte', 'Firebase', 'Tailwind'], difficulty: 'Beginner', status: 'Recruiting', type: 'Community', contributors: 7, teamSize: 9, owner: 'Elena García', ownerUsername: 'elenag', updated: '6 hours ago', roles: ['Full-stack Developer'], popular: 74,
  },
  {
    id: 'opensource-radar', name: 'OpenSource Radar', emoji: 'OR', color: 'cyan',
    description: 'Surface friendly first issues and help contributors find open-source projects that fit their goals.',
    longDescription: 'OpenSource Radar makes the first step into open source feel approachable. We curate signals from issue trackers and project docs into a discovery workflow built for humans.',
    stack: ['TypeScript', 'GraphQL', 'Vercel'], difficulty: 'Advanced', status: 'In progress', type: 'Open source', contributors: 11, teamSize: 14, owner: 'Leo Martin', ownerUsername: 'leomartin', updated: '2 days ago', roles: ['Backend Developer'], popular: 97,
  },
]

export const developers = [
  { username: 'alexrivera', name: 'Alex Rivera', initials: 'AR', color: 'purple', title: 'Product-minded frontend engineer', bio: 'I like turning complex workflows into calm, useful interfaces.', location: 'Austin, TX', skills: ['React', 'TypeScript', 'Design systems'], projects: 8, availability: 'Open to collaborate', experience: 'Senior', github: 'alexrivera', linkedin: 'alex-rivera', accent: 'purple' },
  { username: 'mayac', name: 'Maya Chen', initials: 'MC', color: 'orange', title: 'Full-stack developer & maintainer', bio: 'Building tools that make teams and open source healthier.', location: 'Vancouver, CA', skills: ['Node.js', 'React', 'PostgreSQL'], projects: 12, availability: 'Looking for teammates', experience: 'Senior', github: 'mayac', linkedin: 'maya-chen', accent: 'orange' },
  { username: 'arjunrao', name: 'Arjun Rao', initials: 'AR', color: 'blue', title: 'Backend engineer who loves good docs', bio: 'Python, APIs, and making the hard parts feel straightforward.', location: 'Bengaluru, IN', skills: ['Python', 'Django', 'Docker'], projects: 6, availability: 'Open to collaborate', experience: 'Mid-level', github: 'arjunrao', linkedin: 'arjunrao', accent: 'blue' },
  { username: 'priyanair', name: 'Priya Nair', initials: 'PN', color: 'teal', title: 'Platform engineer', bio: 'I build reliable systems and occasionally obsess over CI times.', location: 'London, UK', skills: ['Python', 'AWS', 'Kubernetes'], projects: 10, availability: 'Available part-time', experience: 'Senior', github: 'priyanair', linkedin: 'priya-nair', accent: 'teal' },
  { username: 'noraw', name: 'Nora Wilson', initials: 'NW', color: 'pink', title: 'Designer who prototypes in code', bio: 'Research, interaction design, and a little bit of frontend magic.', location: 'Portland, OR', skills: ['Figma', 'React', 'UX research'], projects: 7, availability: 'Open to collaborate', experience: 'Mid-level', github: 'noraw', linkedin: 'nora-wilson', accent: 'pink' },
  { username: 'samirp', name: 'Samir Patel', initials: 'SP', color: 'indigo', title: 'ML engineer & curious builder', bio: 'Exploring practical AI products with careful, human-centered UX.', location: 'Toronto, CA', skills: ['Python', 'FastAPI', 'Machine learning'], projects: 5, availability: 'Looking for teammates', experience: 'Mid-level', github: 'samirp', linkedin: 'samir-patel', accent: 'indigo' },
]

export const activities = [
  { person: 'Alex Rivera', initials: 'AR', color: 'purple', action: 'joined RepoAnalytics', time: '12 minutes ago' },
  { person: 'Sarah Kim', initials: 'SK', color: 'orange', action: 'opened a new issue in OpenStudy', time: '48 minutes ago' },
  { person: 'Michael Torres', initials: 'MT', color: 'blue', action: 'updated the README in DevBoard', time: '2 hours ago' },
  { person: 'Maya Chen', initials: 'MC', color: 'teal', action: 'published a new project', time: 'Yesterday' },
]

export const currentUser = { name: 'Alex Rivera', username: 'alexrivera', initials: 'AR', color: 'purple', skills: ['React', 'TypeScript', 'Node.js'] }

export const myProjects = [projects[0], projects[2], projects[5]]

export const applications = [
  { id: 1, kind: 'sent', project: 'OpenSource Radar', person: 'Leo Martin', role: 'Frontend Developer', date: 'Aug 8, 2026', status: 'Pending', color: 'cyan' },
  { id: 2, kind: 'sent', project: 'CampusHub', person: 'Elena García', role: 'Full-stack Developer', date: 'Aug 2, 2026', status: 'Accepted', color: 'green' },
  { id: 3, kind: 'received', project: 'RepoAnalytics', person: 'Alex Rivera', role: 'Frontend Developer', date: 'Aug 10, 2026', status: 'Pending', color: 'purple' },
  { id: 4, kind: 'received', project: 'RepoAnalytics', person: 'Noah Williams', role: 'Data Engineer', date: 'Aug 9, 2026', status: 'Rejected', color: 'orange' },
]

export const projectTeam = [developers[1], developers[0], developers[2], developers[4]]
