export type NavCategory = 'analytics' | 'scientific' | 'knowledge' | 'system';

export interface NavItem {
  id: string;
  label: string;
  path: string;
  iconName: string;
  category: NavCategory;
  badge?: string;
  isBeta?: boolean;
}

export interface NavGroup {
  category: NavCategory;
  title: string;
  items: NavItem[];
}
