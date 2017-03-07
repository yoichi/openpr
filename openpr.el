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
  (let ((hash (cond ((bound-and-true-p magit-blame-mode)
		     (magit-blame-chunk-get :hash))
		    (t
		     (current-word)))))
    (if (string-match openpr-commit-hash-regexp hash)
	(call-process "openpr" nil nil nil hash)
      (error "cannot detect commit hash from current point"))))

(provide 'openpr)

;;; openpr.el ends here
