import { initializeApp } from "https://www.gstatic.com/firebasejs/9.6.10/firebase-app.js";
import { getFirestore, collection, query, onSnapshot, doc, getDoc, setDoc, serverTimestamp, addDoc,updateDoc, where, orderBy, getDocs, deleteDoc} from "https://www.gstatic.com/firebasejs/9.6.10/firebase-firestore.js";
import { getStorage, ref as storageRef, uploadBytes, getDownloadURL } from "https://www.gstatic.com/firebasejs/9.6.10/firebase-storage.js";

const firebaseConfig = {
    apiKey: "AIzaSyAzV7CPVJJbgteozTbjdlIcyt85Kbuxd90",
    authDomain: "uainternetolimp-41dd1.firebaseapp.com",
    projectId: "uainternetolimp-41dd1",
    storageBucket: "uainternetolimp-41dd1.appspot.com",
    messagingSenderId: "545486624571",
    appId: "1:545486624571:web:4a543063a04b43e5bb091e",
    measurementId: "G-MJBJXCE1SJ"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const storage = getStorage(app);

export async function fetchAllUsers() {
    const usersQuery = query(collection(db, "users"));
    const querySnapshot = await getDocs(usersQuery);
    return querySnapshot.docs.map(doc => doc.data());
}

export async function fetchAllRegistrations() {
    const registrationsQuery = query(collection(db, "school_registrations"));
    const querySnapshot = await getDocs(registrationsQuery);
    return querySnapshot.docs.map(doc => doc.data());
}