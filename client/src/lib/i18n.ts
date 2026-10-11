
import type { Language } from "@/components/LanguageProvider";

type Labels = {
  home: string;
  report: string;
  profile: string;
  tagline: string;
  statuses: Record<string, string>;
};

export const messages: Record<Language, Labels> = {
  en: {
    home: "Home",
    report: "Report",
    profile: "Profile",
    tagline: "Report it. Track it. Get it fixed.",
    statuses: {
      submitted: "Submitted",
      verified: "Verified",
      assigned: "Assigned",
      in_progress: "In progress",
      resolved: "Resolved",
    },
  },

  hi: {
    home: "होम",
    report: "शिकायत",
    profile: "प्रोफ़ाइल",
    tagline: "शिकायत करें। प्रगति देखें। समाधान पाएं।",
    statuses: {
      submitted: "दर्ज",
      verified: "सत्यापित",
      assigned: "सौंपा गया",
      in_progress: "काम जारी",
      resolved: "समाधान हुआ",
    },
  },

  mr: {
    home: "मुख्यपृष्ठ",
    report: "तक्रार",
    profile: "प्रोफाइल",
    tagline: "तक्रार नोंदवा. प्रगती पाहा. समस्या सोडवा.",
    statuses: {
      submitted: "नोंदवली",
      verified: "पडताळली",
      assigned: "सोपवली",
      in_progress: "काम सुरू",
      resolved: "निराकरण झाले",
    },
  },
};
