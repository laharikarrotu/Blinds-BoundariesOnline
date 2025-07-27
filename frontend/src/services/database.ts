import { 
  collection, 
  doc, 
  setDoc, 
  getDoc, 
  getDocs, 
  addDoc, 
  updateDoc, 
  deleteDoc, 
  query, 
  where, 
  orderBy, 
  limit,
  Timestamp 
} from 'firebase/firestore';
import { db } from '../firebase-config';

// Types
export interface User {
  id: string;
  email: string;
  name: string;
  createdAt: Timestamp;
  lastLogin: Timestamp;
}

export interface Favorite {
  id: string;
  userId: string;
  imageId: string;
  blindName: string;
  blindType?: string;
  color: string;
  material?: string;
  resultUrl: string;
  createdAt: Timestamp;
}

export interface History {
  id: string;
  userId: string;
  imageId: string;
  blindName: string;
  blindType?: string;
  color: string;
  material?: string;
  resultUrl: string;
  createdAt: Timestamp;
}

export interface UserPreferences {
  userId: string;
  defaultBlindType: string;
  defaultColor: string;
  defaultMaterial: string;
  theme: 'light' | 'dark';
  notifications: boolean;
}

// Database Service Class
class DatabaseService {
  // Users
  async createUser(userId: string, userData: Omit<User, 'id' | 'createdAt' | 'lastLogin'>): Promise<void> {
    const userRef = doc(db, 'users', userId);
    const user: User = {
      id: userId,
      ...userData,
      createdAt: Timestamp.now(),
      lastLogin: Timestamp.now()
    };
    await setDoc(userRef, user);
  }

  async getUser(userId: string): Promise<User | null> {
    const userRef = doc(db, 'users', userId);
    const userSnap = await getDoc(userRef);
    return userSnap.exists() ? userSnap.data() as User : null;
  }

  async updateUserLastLogin(userId: string): Promise<void> {
    const userRef = doc(db, 'users', userId);
    await updateDoc(userRef, {
      lastLogin: Timestamp.now()
    });
  }

  // Favorites
  async addFavorite(favoriteData: Omit<Favorite, 'id' | 'createdAt'>): Promise<string> {
    const favoritesRef = collection(db, 'favorites');
    const favorite: Omit<Favorite, 'id'> = {
      ...favoriteData,
      createdAt: Timestamp.now()
    };
    const docRef = await addDoc(favoritesRef, favorite);
    return docRef.id;
  }

  async getFavorites(userId: string): Promise<Favorite[]> {
    const favoritesRef = collection(db, 'favorites');
    const q = query(
      favoritesRef,
      where('userId', '==', userId),
      orderBy('createdAt', 'desc')
    );
    const querySnapshot = await getDocs(q);
    return querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }) as Favorite);
  }

  async removeFavorite(favoriteId: string): Promise<void> {
    const favoriteRef = doc(db, 'favorites', favoriteId);
    await deleteDoc(favoriteRef);
  }

  async isFavorite(userId: string, imageId: string): Promise<boolean> {
    const favoritesRef = collection(db, 'favorites');
    const q = query(
      favoritesRef,
      where('userId', '==', userId),
      where('imageId', '==', imageId)
    );
    const querySnapshot = await getDocs(q);
    return !querySnapshot.empty;
  }

  // History
  async addToHistory(historyData: Omit<History, 'id' | 'createdAt'>): Promise<string> {
    const historyRef = collection(db, 'history');
    const history: Omit<History, 'id'> = {
      ...historyData,
      createdAt: Timestamp.now()
    };
    const docRef = await addDoc(historyRef, history);
    return docRef.id;
  }

  async getHistory(userId: string, limitCount: number = 20): Promise<History[]> {
    const historyRef = collection(db, 'history');
    const q = query(
      historyRef,
      where('userId', '==', userId),
      orderBy('createdAt', 'desc'),
      limit(limitCount)
    );
    const querySnapshot = await getDocs(q);
    return querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }) as History);
  }

  async clearHistory(userId: string): Promise<void> {
    const historyRef = collection(db, 'history');
    const q = query(historyRef, where('userId', '==', userId));
    const querySnapshot = await getDocs(q);
    
    const deletePromises = querySnapshot.docs.map(doc => deleteDoc(doc.ref));
    await Promise.all(deletePromises);
  }

  // User Preferences
  async getUserPreferences(userId: string): Promise<UserPreferences | null> {
    const prefsRef = doc(db, 'userPreferences', userId);
    const prefsSnap = await getDoc(prefsRef);
    return prefsSnap.exists() ? prefsSnap.data() as UserPreferences : null;
  }

  async updateUserPreferences(userId: string, preferences: Partial<UserPreferences>): Promise<void> {
    const prefsRef = doc(db, 'userPreferences', userId);
    await setDoc(prefsRef, { userId, ...preferences }, { merge: true });
  }

  async createDefaultPreferences(userId: string): Promise<void> {
    const defaultPrefs: UserPreferences = {
      userId,
      defaultBlindType: 'horizontal',
      defaultColor: '#4A5568',
      defaultMaterial: 'fabric',
      theme: 'light',
      notifications: true
    };
    await this.updateUserPreferences(userId, defaultPrefs);
  }
}

export const databaseService = new DatabaseService();
export default databaseService; 