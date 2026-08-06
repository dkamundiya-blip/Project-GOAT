import { useNotificationStore } from '../stores/notificationStore';

export function useNotifications() {
  const store = useNotificationStore();
  return {
    notifications: store.notifications,
    unreadCount: store.notifications.filter((n) => !n.read).length,
    addNotification: store.addNotification,
    markAsRead: store.markAsRead,
    clearNotifications: store.clearNotifications,
  };
}
