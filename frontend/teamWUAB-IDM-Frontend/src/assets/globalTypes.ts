// Global Types and Classes

export class Permission {
    name: string;
    resource: string;
    expiry_time: number;
    approved_time?: number;
    is_inherent: boolean;

    constructor(
        name: string,
        resource: string,
        expiry_time: number,
        is_inherent: boolean = false
    ) {
        this.name = name;
        this.resource = resource;
        this.expiry_time = expiry_time;
        this.is_inherent = is_inherent;
    }
}


export class User {
    uid: string;
    first_name: string;
    last_name: string;
    persistent_perms: Permission[];
    active_perms: Permission[];
    denied_perms: Permission[];
    requestable_resources: Permission[];
    supervisors_uid: string[];
    co_supervisors_uid: string[];
    sent_requests: PermissionRequest[]; // Define the type of sent_requests appropriately
    received_requests: PermissionRequest[]; // Define the type of received_requests appropriately
    has_co_supervisors: boolean;
    can_receive_requests: boolean;

    constructor(
        uid: string,
        first_name: string,
        last_name: string,
        persistent_perms: Permission[],
        requestable_resources: Permission[],
        supervisors_uid: string[],
        can_receive_requests: boolean = true,
        co_supervisors_uid: string[] = []
    ) {
        this.uid = uid;
        this.first_name = first_name;
        this.last_name = last_name;
        this.persistent_perms = persistent_perms;
        this.active_perms = [];
        this.denied_perms = [];
        this.requestable_resources = requestable_resources;
        this.supervisors_uid = supervisors_uid;
        this.co_supervisors_uid = co_supervisors_uid;
        this.sent_requests = [];
        this.received_requests = [];
        this.has_co_supervisors = co_supervisors_uid.length > 0;
        this.can_receive_requests = can_receive_requests;
    }
}



export class PermissionRequest {
    id?: number;
    requester_uid?: string;
    resource: string;
    time_sent?: number;
    reason: string;
    duration: number;
    ip?: string;
    analysis?: string;

    constructor(
        resource: string,
        reason: string,
        duration: number,
    ) {
        this.resource = resource;
        this.reason = reason;
        this.duration = duration;
    }

}
export enum PermissionStatus {
    PENDING = 'PENDING',
    GRANTED = 'GRANTED',
    DENIED = 'DENIED'
}
