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
                        <v-select :items="['Test', 'Cheese']" v-model="selectedPermission"></v-select>
                        <v-btn @click="cheeseCount++" prepend-icon="mdi-cheese">Cheese Counter: {{ cheeseCount }}</v-btn>
                    </v-card-text>
                </v-card>
            </v-col>
            <v-col>
                <v-card title="Settings" class="pa-4">
                    <v-form ref="submissionSettings">
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
    import {ref, Ref, computed, onMounted} from 'vue';
    import { Api } from "@/services/api"
    import { User } from "@/assets/globalTypes"
    let cheeseCount: Ref<number> = ref(0)
    let periodOfDay: Ref<number> = ref(0)
    let selectedPermission: Ref<string> = ref("Test")
    let durationInMinutes: Ref<number> = ref(5)
    let justificationString: Ref<string> = ref("")


    function submit(): void {
        console.log(JSON.stringify(new PermissionRequest(selectedPermission.value, Date.now(), justificationString.value, durationInMinutes.value * 60)))
        Api.post("/request", '{"resource":"Test","time":1697347873857,"reason":"","duration":300}')
        Api.get("/test").then((res: User) => {
            console.log(res)
        })
    }

</script>
