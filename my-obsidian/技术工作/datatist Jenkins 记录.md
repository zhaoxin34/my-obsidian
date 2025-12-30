# 待构建的工程存储在jenkins pod的目录

*~/workspace/jenkins/data/workspace/cl_v3_datatist-wolf-app-dc

# 如何调用某个pipeline示例

```groovy
String gitUrl = "https://gitlab.datatist.cn/datatist/datatist-wolf-manager-v4"
String k8sNamespace = "dev-wolf"

pipeline {
    agent any
    parameters {
        string(name: 'tag', description: '发布的版本或者分支', defaultValue: "master")
        choice(name: 'uploadToFtp', description: '是否上传至ftp', choices: ['否', '是'])
    }

    stages {
        stage('Call v4_spring_cloud_common') {
            steps {
                script {
                    build job: 'v4_spring_cloud_common',
                          wait: true,
                          parameters: [
                              string(name: 'gitUrl', value: "$gitUrl"),
                              string(name: 'tag', value: "${params.tag}"),
                              string(name: 'uploadToFtp', value: "${params.uploadToFtp}"),
                              string(name: 'k8sNamespace', value: "${k8sNamespace}")
                          ]
                }
            }
        }
    }
}
```

