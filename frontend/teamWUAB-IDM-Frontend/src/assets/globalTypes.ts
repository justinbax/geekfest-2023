// Global Types and Classes

export class Permission {
    name?: string
    desc?: string
    resource: string
    holder: User
    expiry: number
    approved: number
    isInherent: boolean
    constructor(resource: string, holder: User, expiry: number, approved: number, isInherent: boolean, name: string, desc: string) {
        this.resource = resource
        this.holder = holder
        this.expiry = expiry
        this.approved = approved
        this.isInherent = isInherent
        this.name = name
        this.desc = desc
    }
}

export class User {
    uid: string
    first_name: string
    last_name: string
    persistent_perms?: Permission[]
    active_perms?: Permission[]
    supervisors?: User[]
    co_supervisors?: User[]
    recieved_requests?: PermissionRequest[]
    sent_requests?: PermissionRequest[]
    has_co_supervisors?: boolean
    can_recieve_requests: boolean

    constructor(uid: string, first_name: string, last_name: string, can_recieve_requests: boolean) {
        this.uid = uid
        this.first_name = first_name
        this.last_name = last_name
        this.can_recieve_requests = can_recieve_requests
    }

}


export class PermissionRequest {
    id?: number
    resource: string
    time: number
    reason: string
    duration:  number
    ip?: string
    status: PermissionStatus

    constructor(resource: string, time: number, reason: string, duration: number, status: PermissionStatus, ip?: string) {
        this.resource = resource
        this.time = time
        this.reason = reason
        this.duration = duration
        this.ip = ip
        this.status = status
    }

}
let test: User = new User("test", "Chris", "Yang", true)


export enum PermissionStatus {
    PENDING = 'PENDING',
    GRANTED = 'GRANTED',
    DENIED = 'DENIED'
}
