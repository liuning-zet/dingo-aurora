pipeline {
    agent {
        node {
            label "dingo_stack"
        }
    }
    environment {
      SOURCE_DIR = '/data/pipeline_demo'
      BUILD_DATE = sh(script: 'date +%Y%m%d', returnStdout: true).trim()
      IMAGE_TAG = "${branch ? branch : 'main'}-${BUILD_DATE}"
    }
    triggers {
        GenericTrigger (
            causeString: 'Triggered', 
            genericVariables: [
              [key: 'ref', value: '$.ref'],
              [key: 'action', value: '$.action'],
              [key: 'merge_commit', value: '$.pull_request.merge_commit_sha'],
              [key: 'branch', value: '$.workflow_run.head_branch'],
              [key: 'repo', value: '$.repository.name'],
              [key: 'pull_request_title', value: '$.pull_request.title'],
              [key: 'result', value: '$.workflow_run.conclusion']
            ], 
            printContributedVariables: true, 
            printPostContent: true,
            regexpFilterExpression: 'completed\\smain\\ssuccess',
            regexpFilterText: '$action $branch $result',
            token: 'dingo-command'
        )
    }

    stages {
        stage('Milestone: kill older builds') {
            steps {
                milestone(1)
            }
        }
        stage('docker build') {
            when {
                anyOf { branch 'develop'; branch 'main' }
            }
            
            agent {
                node {
                    label "dingo_stack"
                }
            }
            steps {
                echo "build image harbor.zetyun.cn/dingostack/dingo-command:${IMAGE_TAG}"
                withCredentials([usernamePassword(credentialsId: 'harbor_credential', usernameVariable: 'HARBOR_USERNAME', passwordVariable: 'HARBOR_PASSWORD')]) {
                    sh 'podman login harbor.zetyun.cn -u $HARBOR_USERNAME -p $HARBOR_PASSWORD'
                }
                sh 'podman build -t harbor.zetyun.cn/dingostack/dingo-command:${IMAGE_TAG} -f docker/Dockerfile-local .'
                echo "Tagging dingo-command image as harbor.zetyun.cn/dingostack/dingo-command:${IMAGE_TAG}"
                retry(3) {
                    sh 'podman push harbor.zetyun.cn/dingostack/dingo-command:${IMAGE_TAG}'
                }
                sh 'podman tag harbor.zetyun.cn/dingostack/dingo-command:${IMAGE_TAG} harbor.zetyun.cn/openstack/dingo-command:${IMAGE_TAG}'
                retry(3) {
                    sh 'podman push harbor.zetyun.cn/openstack/dingo-command:${IMAGE_TAG}'
                }
            }
            
        }
        stage('Pull and Tag Images') {
            when {
                anyOf { branch 'develop'; branch 'main' }
            }

            agent {
                node {
                    label "dingo_stack"
                }
            }
            steps {
                echo 'podman push to second registry'
                sh 'podman tag harbor.zetyun.cn/dingostack/dingo-command:${IMAGE_TAG} 10.220.56.101:5000/dockerproxy.zetyun.cn/quay.nju.edu.cn/openstack.kolla/dingo-command:${IMAGE_TAG}'
                sh 'podman push 10.220.56.101:5000/dockerproxy.zetyun.cn/quay.nju.edu.cn/openstack.kolla/dingo-command:${IMAGE_TAG} --tls-verify=false'
            }

        }
        stage('Deploy to test'){
            when {
                branch 'main'
            }
            parallel {
               
                stage('pull image') {
                    agent {
                        node {
                            label "dingo_stack"
                        }
                    }
            
                    steps {
                        echo "pull dingo-command images to dev cluster(56.4)"
                        dir('/home/cicd/kolla-ansible/tools') {
                            sh 'ansible-playbook  -e @/home/cicd/envs/test-regionone/globals.yml -e @/home/cicd/envs/test-regionone/passwords.yml  --tags dingo-command -e openstack_tag=${IMAGE_TAG} -e kolla_action=pull ../ansible/site.yml  --inventory /home/cicd/envs/test-regionone/multinode -e CONFIG_DIR=/home/cicd/envs/test-regionone -e docker_namespace=openstack -e docker_registry=harbor.zetyun.cn'
                            echo 'deploy images to develop '
                            sh 'ansible-playbook  -e @/home/cicd/envs/test-regionone/globals.yml -e @/home/cicd/envs/test-regionone/passwords.yml  --tags dingo-command -e openstack_tag=${IMAGE_TAG} -e kolla_action=upgrade ../ansible/site.yml  --inventory /home/cicd/envs/test-regionone/multinode -e CONFIG_DIR=/home/cicd/envs/test-regionone -e docker_namespace=openstack -e docker_registry=harbor.zetyun.cn'
                        }
                    }
                }
                stage('pull image on integration test cluster(56.7)') {
                    agent {
                        node {
                            label "dingo_stack"  // 请替换为实际的第二个节点标签
                        }
                    }

                    steps {
                        echo "pull dingo-command images to integration test（56.7）"
                        dir('/home/cicd/kolla-ansible/tools') {
                            sh 'ansible-playbook -e @/home/cicd/envs/integration_test_env/globals.yml -e @/home/cicd/envs/integration_test_env/passwords.yml --tags dingo-command -e openstack_tag=${IMAGE_TAG} -e CONFIG_DIR=/home/cicd/envs/integration_test_env -e kolla_action=pull ../ansible/site.yml  --inventory /home/cicd/envs/integration_test_env/multinode -e docker_namespace=openstack -e docker_registry=harbor.zetyun.cn'
                            echo 'deploy images to develop on second node'
                            sh 'ansible-playbook -e @/home/cicd/envs/integration_test_env/globals.yml -e @/home/cicd/envs/integration_test_env/passwords.yml --tags dingo-command -e openstack_tag=${IMAGE_TAG} -e CONFIG_DIR=/home/cicd/envs/integration_test_env -e kolla_action=upgrade ../ansible/site.yml  --inventory /home/cicd/envs/integration_test_env/multinode -e docker_namespace=openstack -e docker_registry=harbor.zetyun.cn'
                        }
                    }

                    // ==================== 自动触发接口自动化测试 ====================
                    post {
                        success {
                            script {
                                echo "集成测试环境 (56.7) 部署成功。等待120秒后触发自动化测试..."

                                // 1. 等待120秒，让服务有足够的时间启动和稳定
                                sleep 120

                                echo "开始触发下游自动化测试任务..."

                                // 2. 获取 Git 相关信息
                                def commitId = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()
                                def commitAuthor = sh(returnStdout: true, script: "git log -1 --pretty=format:'%an'").trim()

                                // 3. 触发下游项目，并传递参数
                                build(
                                    job: 'anc_http_autotest', // <== 请确保这里是正确的自动化测试项目名称
                                    wait: true,
                                    parameters: [
                                        string(name: 'GIT_BRANCH', value: env.BRANCH_NAME),
                                        string(name: 'GIT_COMMIT_ID', value: commitId),
                                        string(name: 'GIT_COMMIT_USER', value: commitAuthor)
                                    ]
                                )
                            }
                        }
                        failure {
                            // （可选）如果这个 stage 失败了，可以在这里添加特定的通知
                            echo "集成测试环境 (56.7) 部署失败！"
                        }
                    }
                }

                stage('pull image on functional test cluster(244.176)') {
                    agent {
                        node {
                            label "dingo_stack"  // 请替换为实际的第二个节点标签
                        }
                    }

                    steps {
                        echo "pull dingo-command images to test on second node"
                        dir('/home/cicd/kolla-ansible/tools') {
                            sh 'ansible-playbook -e @/home/cicd/envs/functional_test_env/globals.yml -e @/home/cicd/envs/functional_test_env/passwords.yml --tags dingo-command -e openstack_tag=${IMAGE_TAG} -e CONFIG_DIR=/home/cicd/envs/functional_test_env -e kolla_action=pull ../ansible/site.yml  --inventory /home/cicd/envs/functional_test_env/multinode -e docker_namespace=openstack -e docker_registry=harbor.zetyun.cn'
                            echo 'deploy images to develop on second node'
                            sh 'ansible-playbook -e @/home/cicd/envs/functional_test_env/globals.yml -e @/home/cicd/envs/functional_test_env/passwords.yml --tags dingo-command -e openstack_tag=${IMAGE_TAG} -e CONFIG_DIR=/home/cicd/envs/functional_test_env -e kolla_action=upgrade ../ansible/site.yml  --inventory /home/cicd/envs/functional_test_env/multinode -e docker_namespace=openstack -e docker_registry=harbor.zetyun.cn'
                        }
                    }
                }
            }
        }

        stage('notify autotest') {
            when {
                branch 'main'
            }
            agent {
                node {
                    label "dingo_stack"
                }
            }
            steps {
                script {
                    echo "start notify autotest"
                    sh ' /home/cicd/cronjob-trigger-autotest -token "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6IkFQSS1UT0tFTjphdXRvdGVzdC1hcGktdG9rZW4iLCJ2ZXJzaW9uIjoiMSIsImlzcyI6ImFwaVRva2VuSXNzdWVyIn0.2yrCOmQ-L6lzrrdLTcGx-i985829de4oVAOmHLni7k0" -jobs "unite-autotest:unite-beijing-1"'
                }
            }
        }

        stage('deploy dingoOps to dev'){
            when {
                anyOf { branch 'develop'; branch 'stable/2023.2' }
            }

            parallel {
              
                stage('pull cinder') {
                    agent {
                        node {
                            label "dingo_stack"
                        }
                    }
                    steps {
                        echo "pull cinder images to dev"
                        sh 'kolla-ansible -i /root/multinode pull --tag cinder -e openstack_tag=${branch}'
                        echo 'deploy images to develop '
                        sh 'kolla-ansible -i /root/multinode upgrade --tag cinder -e openstack_tag=${branch}'
                    }
                }
            }
        }
    }

}
