import { writable } from 'svelte/store';

// 1. "User 데이터는 이렇게 생겼다"라고 정의 (인터페이스)
export interface User {
    id: string;
    name: string;
    role?: string; // role은 있을 수도 있고 없을 수도 있음 (옵션)
}

// 2. <User | null>을 붙여서 "User 데이터 또는 null(빈 값)이 들어간다"고 명시
export const user = writable<User | null>(null);