fn test() {
    let mut x86: HashMap<String, Vec<String>> = HashMap::new();
    let mut x86_64: HashMap<String, Vec<String>> = HashMap::new();

    x86.insert(
        "x86".to_string(),
        vec!["ubuntu".to_string(), "arch".to_string()],
    );
    x86_64.insert(
        "x86_64".to_string(),
        vec!["windows".to_string(), "darwin".to_string()],
    );

    let mut dep_1: HashMap<String, String> = HashMap::new();
    let mut dep_2: HashMap<String, String> = HashMap::new();

    dep_1.insert("test-2".to_string(), "4.5.6".to_string());
    dep_2.insert("test-3".to_string(), "7.8.9".to_string());

    let mut dep_3: HashMap<String, String> = HashMap::new();
    let mut dep_4: HashMap<String, String> = HashMap::new();

    dep_3.insert("test-4".to_string(), "6.9.0".to_string());
    dep_4.insert("test-5".to_string(), "4.2.0".to_string());

    let mut sha256: HashMap<String, String> = HashMap::new();
    let mut md5: HashMap<String, String> = HashMap::new();

    sha256.insert("sha256".to_string(), "123456789".to_string());
    md5.insert("md5".to_string(), "987654321".to_string());

    let pkg_info = PkgInfo {
        name: vec!["test".to_string()],
        ver: "1.2.3".to_string(),
        desc: Some("test package".to_string()),
        license: Some(vec!["Public Domain".to_string()]),
        pkg: Some(vec![PkgMain {
            supports: Some(vec![x86, x86_64]),
            repos: Some(vec!["abc://test.xyz/test/repo".to_string(), "abc://test.xyz/test/repo-mirror".to_string()]),
            ver: Some("1.2.3".to_string()),
            deps: Some(vec![dep_1, dep_2]),
            dev_deps: Some(vec![dep_3, dep_4]),
            _type: "binary".to_string(),
            srcs: Some(vec![PkgSrc {
                path: vec![
                    "abc://test.xyz/test/src".to_string(),
                    "abc://test.xyz/test/src-mirror".to_string(),
                ],
                hashes: Some(vec![sha256, md5]),
            }]),
            test: Some(vec![PkgAction {
                name: Some("Print Test - POSIX".to_string()),
                _if: Some(vec![
                    "${os.group} == \"posix\"".to_string(),
                    "${os.group} != \"windows\"".to_string(),
                ]),
                run: Some("echo \"Hello World!\"".to_string()),
            }, PkgAction {
                name: Some("Print Test - Windows".to_string()),
                _if: Some(vec![
                    "${os.group} == \"windows\"".to_string(),
                    "${os.group} != \"posix\"".to_string(),
                ]),
                run: Some("Write-Host \"Hello World!\"".to_string()),
            }]),
            build: None,
            install: None,
            uninstall: None,
        }]),
    };

    let yaml = serde_yaml::to_string(&pkg_info).unwrap();

    bat::PrettyPrinter::new()
        .input_from_bytes(yaml.as_bytes())
        .language("yaml")
        .line_numbers(false)
        .grid(true)
        .theme("Visual Studio Dark+")
        .print()
        .expect("Error: Could not print yaml.");

    return;
}
