export class UserManager {
    private users: string[] = [];

    public addUser(name: string): void {
        this.users.push(name);
    }

    public getUsers(): string[] {
        return this.users;
    }
}

export interface User {
    id: number;
    name: string;
}

const main = () => {
    const manager = new UserManager();
    manager.addUser("Alice");
};
