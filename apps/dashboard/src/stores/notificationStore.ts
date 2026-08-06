import { create } from 'zustand';
import { NotificationItem, NotificationType } from '../types/state';

interface NotificationStoreState {
  notifications: NotificationItem[];
  addNotification: (title: string, message: string, type?: NotificationType) => void;
  markAsRead: (id: string) => void;
  clearNotifications: () => void;
}

export const useNotificationStore = create<NotificationStoreState>((set) => ({
  notifications: [
    {
      id: 'notif-1',
      title: 'System Initialized',
      message: 'Project GOAT Dashboard Control Room Foundation Ready.',
      type: 'info',
      timestamp: 'Just now',
      read: false,
    },
  ],
  addNotification: (title, message, type = 'info') =>
    set((state) => ({
      notifications: [
        {
          id: `notif-${Date.now()}`,
          title,
          message,
          type,
          timestamp: new Date().toLocaleTimeString(),
          read: false,
        },
        ...state.notifications,
      ],
    })),
  markAsRead: (id) =>
    set((state) => ({
      notifications: state.notifications.map((n) => (n.id === id ? { ...n, read: true } : n)),
    })),
  clearNotifications: () => set({ notifications: [] }),
}));
