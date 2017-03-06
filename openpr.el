;;; openpr.el --- Open pull request include the commit in a Web browser

;; Copyright (c) 2017 Yoichi NAKAYAMA. All rights reserved.

;;; Code:

(defcustom openpr-commit-hash-regexp "^[[:xdigit:]]\\{4,40\\}$"
  "Regular expression for commit hash."
  :type 'string
  :group 'open-issue)

(defun openpr ()
  "Open pull request include the commit in a Web browser.
The commit hash is read from current point."
  (interactive)
  (let ((cw (current-word)))
    (if (string-match openpr-commit-hash-regexp cw)
	(call-process "openpr" nil nil nil cw)
      (error "current-word is not a commit hash"))))

(provide 'openpr)

;;; openpr.el ends here
