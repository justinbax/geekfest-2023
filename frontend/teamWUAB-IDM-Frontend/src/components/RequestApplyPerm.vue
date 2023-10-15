<template>
    <v-container>
        <v-row>
            <v-col>
                <v-sheet rounded class="pa-6 rounded-lg d-flex flex-column text-center">
                    <div class="text-h1">Apply and Request for an Access</div>
                </v-sheet>
            </v-col>
        </v-row>
        <v-row>
            <v-col>
                <v-card title="Request permission" class="pa-4" >
                    <v-card-text>
                        <v-select v-if="listOfPerms" :items="listOfPerms" v-model="selectedPermission"></v-select>
                        <v-btn @click="cheeseCount++" prepend-icon="mdi-cheese">Cheese Counter: {{ cheeseCount }}</v-btn>
                    </v-card-text>
                </v-card>
            </v-col>
            <v-col>
                <v-card title="Settings" class="pa-4">
                    <v-form ref="submissionSettings" refs="form">
                        <v-slider step="5" max="120" v-model="durationInMinutes" :append="durationInMinutes">
                        <template v-slot:append>
                            {{ durationInMinutes }} minutes
                        </template>
                    </v-slider>
                    <v-textarea clearable label="Justification" v-model="justificationString"></v-textarea>
                    <v-btn @click="submit()">Submit!</v-btn>
                    </v-form>
                </v-card>
            </v-col>
        </v-row>
        <v-row>

        </v-row>
    </v-container>
</template>

<script setup lang="ts">
    import { PermissionRequest, PermissionStatus } from '@/assets/globalTypes';
    import {ref, Ref} from 'vue';
    import { Api } from "@/services/api"
    import { User } from "@/assets/globalTypes"
    let cheeseCount: Ref<number> = ref(0)
    let periodOfDay: Ref<number> = ref(0)
    let selectedPermission: Ref<string | undefined> = ref()
    let durationInMinutes: Ref<number> = ref(5)
    let activeUser = ref()
    let listOfPerms: Ref<any> = ref([])
    let justificationString: Ref<string> = ref("")
        Api.get('/show').then((res) => {
        activeUser.value = new User(
            res.user.uid,
            res.user.first_name,
            res.user.last_name,
            res.user.persistent_perms,
            res.user.requestable_resources,
            res.user.supervisors_uid,
        )
        for (let i: number = 0; i < res.user.active_perms.length; i++) {
            activeUser.value.active_perms.push(res.user.active_perms[i])
        }
        activeUser.value.active_perms.push({
            name: "Test",
            resource: "Test",
            expiry_time: Date.now() + 5000,
            is_inherent: false
        })
        console.log(res.user.requestable_resources.length)
        console.log(res.user.persistent_perms)
         for (let i: number = 0; i < res.user.requestable_resources.length; i++) {
            listOfPerms.value.push(res.user.requestable_resources[i])
        }
        for (let i: number = 0; i < res.user.persistent_perms.length; i++) {
            listOfPerms.value.push(res.user.persistent_perms[i].name)
        }


        console.log(listOfPerms)
    })
    const form = ref(null)
    function submit() {
        if(selectedPermission.value !== undefined){
            Api.post('/request', new PermissionRequest(selectedPermission.value, justificationString.value, durationInMinutes.value*60)).then(
                () => {
                }
            )
        }
    }


</script>
